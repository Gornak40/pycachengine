#!venv/bin/python
from subprocess import Popen, PIPE
from chess import Board
from os import system


class PyCachEngine:
	def __init__(self, path):
		self.engine = Popen(path, universal_newlines=True, stdin=PIPE, stdout=PIPE)
		self.board = Board()
		self._put('uci')
		self._ready()
		self.learn(1000)

	def __del__(self):
		self.engine.kill()

	def _put(self, line):
		if not self.engine.stdin:
			raise BrokenPipeError()
		self.engine.stdin.write(line + '\n')
		self.engine.stdin.flush()

	def _read(self):
		if not self.engine.stdout:
			raise BrokenPipeError()
		return self.engine.stdout.readline().strip()

	def _ready(self):
		self._put('isready')
		while self._read() != 'readyok':
			continue

	def _bestmove(self):
		while True:
			line = self._read()
			if 'bestmove' in line:
				return line.split()[1]

	def learn(self, movetime):
		self._put(f'position fen {self.board.fen()}')
		self._put(f'go movetime {movetime}')
		move = self._bestmove()
		self.board.push_uci(move)
		system('clear')
		print(self.board)
		if not self.board.is_game_over():
			self.learn(movetime)


if __name__ == '__main__':
	try:
		PyCachEngine('./stockfish_13_linux_x64_avx2')
	except KeyboardInterrupt:
		exit()