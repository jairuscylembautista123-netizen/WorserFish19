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

        engine, uci_variant = self._get_engine_and_variant(board)

        if uci_variant:
            engine.configure({"UCI_Variant": uci_variant})

        num_pvs = min(len(legal_moves), 50)

        info_list = engine.analyse(
            board,
            Limit(time=0.15),
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
            board.push(move)
            is_mate = board.is_checkmate()
            board.pop()
            if not is_mate:
                return PlayResult(move, None)

        for entry in worst_to_best:
            pv = entry.get("pv")
            if pv:
                return PlayResult(next(iter(pv)), None)

        return PlayResult(next(iter(legal_moves)), None)

    def quit(self):
        self.stockfish.quit()
        self.fairy.quit()


ExampleEngine = WorserFish19
