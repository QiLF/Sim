/* Final Solver (Work for loopy game either!)
 * Chen Yanqi, Qi Linfeng
 * 1500012829, 1802051275
 */
#ifndef GAME_H
#define GAME_H

#include <iostream>
#include <cstring>
#include <iomanip>
#include <vector>
#include <cmath>
#include <algorithm>
#include <cassert>
#include <map>
#include <queue>
#include <string>
#include <sstream>
#include <set>

using namespace std;

enum value
{
	WIN,
	LOSE,
	TIE,
	DRAW,
	UNKNOWN
};

ostream &operator<<(ostream &stream, const value &vl)
{
	switch (vl)
	{
	case WIN:
	{
		return stream << "WIN";
		break;
	}
	case LOSE:
	{
		return stream << "LOSE";
		break;
	}
	case TIE:
	{
		return stream << "TIE";
		break;
	}
	case DRAW:
	{
		return stream << "DRAW";
		break;
	}
	case UNKNOWN:
	{
		return stream << "UNKNOWN";
		break;
	}
	default:;
	}
}

class Game
{
  protected:
	//map<int, value> ValueMap;
	//map<int, int> RemotenessMap;
	map<int, value> Primitive;

  public:
	map<int, value> ValueMap;
	map<int, int> RemotenessMap;
	string name;	// Game name
	int max_states; // Reserve space
	bool player1_flag;
	int initial_position;
	Game(int _s, int _v, string _str) : max_states(_s), initial_position(_v), name(_str), player1_flag(true){};

	// Need implementation for different games
	virtual bool is_primitive(int position, value &vlu) = 0;
	virtual void generate_moves(vector<int> &moves, int position) = 0;
	virtual int do_move(int position, int move) = 0;
	virtual int undo_move(int position, int move) = 0;
	virtual string position_to_string(int position) = 0;

	// All games need these
	void children(vector<int> &child, int position)
	{
		vector<int> moves;
		generate_moves(moves, position);
		for (auto it = moves.begin(); it != moves.end(); ++it)
		{
			child.push_back(do_move(position, *it));
			undo_move(position, *it);
		}
	}
	value get_value(int position)
	{
		return ValueMap[position];
	}
	int get_remoteness(int position)
	{
		return RemotenessMap[position];
	}
	void generate_Database()
	{
		vector<vector<int>> child(max_states + 1);
		vector<vector<int>> father(max_states + 1);
		int *child_cnt = new int[max_states + 1];
		bool *is_tie = new bool[max_states + 1];
		bool *visit = new bool[max_states + 1];

		queue<int> frontier;
		queue<pair<int, bool>> visitor;

		memset(child_cnt, 0, (max_states + 1) * sizeof(int));
		memset(is_tie, 0, (max_states + 1) * sizeof(bool));
		memset(visit, 0, (max_states + 1) * sizeof(bool));

		vector<int> moves;
		value end_value;

		// visit all valid states and build graph(BFS)
		visitor.push(make_pair(initial_position, true));
		visit[initial_position] = true;
		while (!visitor.empty())
		{
			int curr_position = visitor.front().first;
			player1_flag = visitor.front().second;
			visitor.pop();

			// reach primitive value
			if (Primitive.find(curr_position) != Primitive.end())
				continue;
			else if (is_primitive(curr_position, end_value))
			{
				Primitive[curr_position] = end_value;
				continue;
			}

			moves.clear();

			generate_moves(moves, curr_position);
			for (auto it = moves.begin(); it != moves.end(); ++it)
			{
				int new_position = do_move(curr_position, *it);
				if (!visit[new_position])
				{
					visitor.push(make_pair(new_position, player1_flag));
					visit[new_position] = true;
				}
				// assign edge
				if (find(father[new_position].begin(), father[new_position].end(), curr_position) == father[new_position].end())
					father[new_position].push_back(curr_position);

				if (find(child[curr_position].begin(), child[curr_position].end(), new_position) == child[curr_position].end())
					child[curr_position].push_back(new_position);

				undo_move(new_position, *it);
			}
		}

		// get child count
		for (int i = 0; i <= max_states; ++i)
		{
			child_cnt[i] = child[i].size();
		}

		for (auto it = Primitive.begin(); it != Primitive.end(); ++it)
		{
			ValueMap[(*it).first] = (*it).second;
			RemotenessMap[(*it).first] = 0;
			frontier.push((*it).first);
		}
		// Walk backwards from the primitive values in the tree
		while (!frontier.empty())
		{
			int curr_position = frontier.front();
			frontier.pop();
			switch (ValueMap[curr_position])
			{
			case LOSE:
			{
				for (auto it = father[curr_position].begin(); it != father[curr_position].end(); ++it)
				{
					ValueMap[*it] = WIN;
					--child_cnt[*it];
					if (RemotenessMap.find(*it) == RemotenessMap.end() || RemotenessMap[*it] > RemotenessMap[curr_position] + 1)
						RemotenessMap[*it] = RemotenessMap[curr_position] + 1;
					if (child_cnt[*it] == 0)
						frontier.push(*it);
				}
				break;
			}
			case TIE:
			{
				for (auto it = father[curr_position].begin(); it != father[curr_position].end(); ++it)
				{
					if (ValueMap.find(*it) == ValueMap.end())
					{
						--child_cnt[*it];
						is_tie[*it] = true;
						// TODO: Remoteness for tied game
						if (child_cnt[*it] == 0)
						{
							ValueMap[*it] = TIE;
							frontier.push(*it);
						}
					}
				}
				break;
			}
			case WIN:
			{
				for (auto it = father[curr_position].begin(); it != father[curr_position].end(); ++it)
				{
					if (ValueMap.find(*it) == ValueMap.end())
					{
						--child_cnt[*it];
						if (child_cnt[*it] == 0)
						{
							if (is_tie[*it])
							{
								// TODO: Remoteness for tied game
								ValueMap[*it] = TIE;
							}
							else
							{
								int max_remoteness = -1;
								for (auto it2 = child[*it].begin(); it2 != child[*it].end(); ++it2)
								{
									if (RemotenessMap[*it2] > max_remoteness)
										max_remoteness = RemotenessMap[*it2];
								}
								ValueMap[*it] = LOSE;
								RemotenessMap[*it] = max_remoteness + 1;
							}
							frontier.push(*it);
						}
					}
					else if (ValueMap[*it] == WIN)
					{
						--child_cnt[*it];
						if (child_cnt[*it] == 0)
							frontier.push(*it);
					}
				}
				break;
			}
			default:;
			}
		}
		for (int i = 0; i <= max_states; ++i)
			if (ValueMap.find(i) == ValueMap.end())
			{
				if (visit[i])
					ValueMap[i] = DRAW;
				else
					ValueMap[i] = UNKNOWN;
			}
		delete[] child_cnt;
		delete[] is_tie;
		delete[] visit;
		player1_flag = true;
	}
	bool is_valid_move(int position, int move)
	{
		vector<int> moves;
		generate_moves(moves, position);
		return find(moves.begin(), moves.end(), move) != moves.end();
	}
};
#endif