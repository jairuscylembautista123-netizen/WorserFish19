import chess
import chess.engine
from chess.engine import PlayResult, Limit
from lib.engine_wrapper import MinimalEngine

class WorserFish19(MinimalEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = chess.engine.SimpleEngine.popen_uci("engines/stockfish/stockfish-linux-x86-64-universal")

    def search(self, board, time_limit, ponder, draw_offered, root_moves):
        legal_moves = list(board.legal_moves)
        if len(legal_moves) == 1:
            return PlayResult(legal_moves[0], None)

        info_list = self.engine.analyse(
            board,
            Limit(time=0.15),
            multipv=len(legal_moves)
        )

        worst_to_best = list(reversed(info_list))

        for entry in worst_to_best:
            move = entry["pv"][0]
            board.push(move)
            is_mate = board.is_checkmate()
            board.pop()
            if not is_mate:
                return PlayResult(move, None)

        return PlayResult(worst_to_best[0]["pv"][0], None)

    def quit(self):
        self.engine.quit()

ExampleEngine = WorserFish19
