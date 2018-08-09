/* Some util for Sim game
 * Chen Yanqi, Qi Linfeng
 * 1500012829, 1802051275
 */

#ifndef SIM_H
#define SIM_H

#include "game.h"
#include <fstream>
using namespace std;

// 3^15
bool visit[14348908] = {};

bool visit_step[16] = {};
int idToEdgeX[15] = {0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4};
int idToEdgeY[15] = {1, 2, 3, 4, 5, 2, 3, 4, 5, 3, 4, 5, 4, 5, 5};
int edgeToId[6][6] = {{-1, 0, 1, 2, 3, 4}, {0, -1, 5, 6, 7, 8}, {1, 5, -1, 9, 10, 11}, {2, 6, 9, -1, 12, 13}, {3, 7, 10, 12, -1, 14}, {4, 8, 11, 13, 14, -1}};

struct info
{
	info(int _p, int _s, int _o) : pos(_p), step(_s), offset(_o){};
	int pos;
	int step;
	int offset;
};
class Sim : public Game
{
	set<int> Hashmap[3730];

	// displacement, used for saving memory, but takes more time
	vector<int> disp;

  public:
	Sim() : Game(-1, 0, "Sim")
	{
		generate_Hashmap();
		generate_Database();
		save_database();
	}
	void generate_Hashmap()
	{
		int init_pos = 0, init_step = 0;
		int id = 1;
		queue<info> Q;
		Q.push(info(init_pos, init_step, 0));
		visit[0] = true;
		visit_step[0] = true;
		Hashmap[0].insert(0);
		disp.reserve(17);
		disp.push_back(0);
		vector<int> moves;
		int per[6] = {0, 1, 2, 3, 4, 5};

		while (!Q.empty())
		{
			int curr_pos = Q.front().pos;
			int curr_step = Q.front().step;
			int curr_offset = Q.front().offset;
			Q.pop();
			value v;

			// Reach primitive value
			if (is_unhash_primitive(curr_pos, v))
			{
				Primitive[curr_offset] = WIN;
				continue;
			}
			moves.clear();
			generate_unhash_moves(moves, curr_pos);
			for (auto i = moves.begin(); i != moves.end(); ++i)
			{
				int new_pos = do_unhash_move(curr_pos, *i, curr_step + 1);
				if (visit[new_pos])
					continue;

				// Find all isomorphic graphs and mark them
				if (!visit_step[curr_step + 1])
				{
					visit_step[curr_step + 1] = true;
					disp.push_back(id);
				}

				Q.push(info(new_pos, curr_step + 1, id));
				sort(per, per + 6);
				int _pos, canon_pos;

				// Go through all the permutation of vertices
				do
				{
					canon_pos = 0;
					_pos = new_pos;
					for (int i = 0; i < 15; ++i)
					{
						int t = _pos % 3;
						canon_pos += t * int(round(pow(3, edgeToId[per[idToEdgeX[i]]][per[idToEdgeY[i]]])));
						_pos = _pos / 3;
					}
					Hashmap[id].insert(canon_pos);
					visit[canon_pos] = true;
				} while (next_permutation(per, per + 6));
				++id;
			}
		}
		disp.push_back(id);
		max_states = id;
	}

	int make_hash(int position)
	{
		int stepcnt = 0;
		int tpos = position;
		for (int i = 0; i < 15; ++i)
		{
			if (tpos % 3 != 0)
				++stepcnt;
			tpos /= 3;
		}
		for (int i = disp[stepcnt]; i < disp[stepcnt + 1]; ++i)
			if (Hashmap[i].find(position) != Hashmap[i].end())
				return i;
		assert(false);
	}

	int make_dehash(int id)
	{
		return *(Hashmap[id].begin());
	}

	void generate_unhash_moves(vector<int> &moves, int position)
	{
		for (int i = 0; i < 15; ++i)
		{
			if (position % 3 == 0)
				moves.push_back(i);
			position /= 3;
		}
	}
	int do_unhash_move(int position, int move, int step)
	{
		int id = (step % 2) ? 1 : 2;
		int newPosition = position;
		newPosition += id * int(round(pow(3, move)));
		return newPosition;
	}
	int undo_unhash_move(int position, int move, int step)
	{
		int id = (step % 2) ? 1 : 2;
		int newPosition = position;
		newPosition -= id * int(round(pow(3, move)));
		return newPosition;
	}
	bool is_unhash_primitive(int position, value &vlu)
	{
		bool mp[2][6][6];
		memset(mp, 0, sizeof(mp));
		int pos = position;
		vlu = WIN;
		int tr, tc;
		for (int i = 0; i < 15; ++i)
		{
			tr = idToEdgeX[i], tc = idToEdgeY[i];
			if (pos % 3 == 1)
			{
				mp[0][tr][tc] = mp[0][tc][tr] = true;
				for (int j = 0; j < 6; ++j)
				{
					if (mp[0][j][tr] && mp[0][j][tc])
						return true;
				}
			}
			else if (pos % 3 == 2)
			{
				mp[1][tr][tc] = mp[1][tc][tr] = true;
				for (int j = 0; j < 6; ++j)
				{
					if (mp[1][j][tr] && mp[1][j][tc])
						return true;
				}
			}
			pos /= 3;
		}
		return false;
	}
	bool is_primitive(int id, value &vlu)
	{
		if (Primitive.find(id) != Primitive.end())
		{
			vlu = WIN;
			return true;
		}
		return false;
	}
	void generate_moves(vector<int> &moves, int id)
	{
		int position = make_dehash(id);
		generate_unhash_moves(moves, position);
	}
	int do_move(int id, int move)
	{
		int position = make_dehash(id);
		int step = 0;
		int tpos = position;
		for (int i = 0; i < 15; ++i)
		{
			if (tpos % 3 != 0)
				++step;
			tpos /= 3;
		}
		int new_position = do_unhash_move(position, move, step + 1);

		return make_hash(new_position);
	}
	int undo_move(int id, int move)
	{
		return 0;
	}
	string position_to_string(int position)
	{
		return "";
	}

	void save_database()
	{
		ofstream hash_file("hash", ios::trunc | ios::binary);
		ofstream value_file("value.txt", ios::trunc);
		ofstream remt_file("remt.txt", ios::trunc);
		if (hash_file.is_open())
		{
			for (int i = 0; i < 3729; ++i)
				for (auto it = Hashmap[i].begin(); it != Hashmap[i].end(); ++it)
				{
					int temp = *it;
					hash_file.write(reinterpret_cast<char *>(&temp), sizeof(int));
					hash_file.write(reinterpret_cast<char *>(&i), sizeof(int));
				}
			hash_file.close();
		}
		if (value_file.is_open())
		{
			for (int i = 0; i < 3729; ++i)
				value_file << ValueMap[i] << endl;
			value_file.close();
		}
		if (remt_file.is_open())
		{
			for (int i = 0; i < 3729; ++i)
				remt_file << RemotenessMap[i] << endl;
			remt_file.close();
		}
	}
};
#endif
