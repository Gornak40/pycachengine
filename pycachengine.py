#!venv/bin/python
from subprocess import Popen, PIPE
from chess import Board
from os import system
from unqlite import UnQLite


class PyCachEngine:
	def __init__(self, path, db_path, options=dict()):
		self.board = Board()
		self.db = UnQLite(db_path)
		self.engine = Popen(path, universal_newlines=True, stdin=PIPE, stdout=PIPE)
		self._put('uci')
		self._ready()
		for option, val in options.items():
			self._set_option(option, val)
		self.num_games = 1
		while True:
			self.board.reset()
			self.learn(100)

	def __del__(self):
		self.db.close()
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
			if 'depth' in line:
				depth = int(line.split()[2])
			if 'bestmove' in line:
				move = line.split()[1]
				return (move, depth)

	def _set_option(self, option, value):
		self._put(f'setoption option {option} value {value}')

	def _store(self, new_fen, move, depth):
		with self.db.transaction():
			if new_fen in self.db:
				_move, _depth = eval(self.db[new_fen].decode('utf-8'))
				print(_move, _depth)
				if int(_depth) >= depth:
					return
			self.db[new_fen] = (move, depth)
		self.db.commit()

	def learn(self, movetime):
		fen = self.board.fen()
		new_fen = ' '.join(fen.split()[:-2])
		self._put(f'position fen {fen}')
		self._put(f'go movetime {movetime}')
		move, depth = self._bestmove()
		self.board.push_uci(move)
		self._store(new_fen, move, depth)
		system('clear')
#		print(fen)
		print(self.board)
		print()
		print('new_fen:', new_fen)
		print('depth:', depth)
		print('move:', move)
		print('db_size:', len(self.db))
		print('num_games:', self.num_games)
		if not self.board.is_game_over():
			self.learn(movetime)
		else:
			result = self.board.outcome().result()
			self.num_games += 1
			print(result)


if __name__ == '__main__':
	try:
		options = {
			'Threads': 4,
			'Hash': 8192
		}
		PyCachEngine(
			path='./stockfish_13_linux_x64_avx2', 
			db_path='pycachengine.db',
			options=options)
	except KeyboardInterrupt:
		exit()