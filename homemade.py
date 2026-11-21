import random
import traceback
import chess
import chess.engine
import chess.variant
from chess.engine import PlayResult, Limit
from lib.engine_wrapper import MinimalEngine


class WorserFish19(MinimalEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stockfish = chess.engine.SimpleEngine.popen_uci(
            "engines/stockfish/stockfish-linux-x86-64-universal"
        )
        self.fairy = chess.engine.SimpleEngine.popen_uci(
            "engines/fairy-stockfish"
        )
        self.last_fairy_variant = None

    def _get_engine_and_variant(self, board):
        uci_variant = getattr(board, "uci_variant", "chess")
        if uci_variant in ("chess", "chess960"):
            return self.stockfish, None
        return self.fairy, uci_variant

    def search(self, board, time_limit, ponder, draw_offered, root_moves):
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return PlayResult(None, None)
        if len(legal_moves) == 1:
            return PlayResult(next(iter(legal_moves)), None)

        try:
            engine, uci_variant = self._get_engine_and_variant(board)

            if uci_variant and uci_variant != self.last_fairy_variant:
                engine.configure({"UCI_Variant": uci_variant})
                self.last_fairy_variant = uci_variant

            num_pvs = min(len(legal_moves), 30)

            info_list = engine.analyse(
                board,
                Limit(time=0.25),
                multipv=num_pvs
            )

            if isinstance(info_list, dict):
                info_list = [info_list]

            worst_to_best = list(reversed(info_list))

            for entry in worst_to_best:
                pv = entry.get("pv")
                if not pv:
                    continue
                move = next(iter(pv))
                if move not in board.legal_moves:
                    continue
                board.push(move)
                is_mate = board.is_checkmate()
                board.pop()
                if not is_mate:
                    return PlayResult(move, None)

            for entry in worst_to_best:
                pv = entry.get("pv")
                if pv:
                    move = next(iter(pv))
                    if move in board.legal_moves:
                        return PlayResult(move, None)

        except Exception:
            print("ERROR IN WORSERFISH SEARCH:")
            traceback.print_exc()

        return PlayResult(random.choice(legal_moves), None)

    def quit(self):
        try:
            self.stockfish.quit()
        except Exception:
            pass
        try:
            self.fairy.quit()
        except Exception:
            pass


ExampleEngine = WorserFish19
