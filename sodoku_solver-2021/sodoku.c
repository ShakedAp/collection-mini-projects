#include <stdio.h>
#include <stdbool.h>
#define BOARD_SIZE 9


int board[BOARD_SIZE][BOARD_SIZE] = {
									{5, 3, 0, 0, 7, 0, 0, 0, 0},
									{6, 0, 0, 1, 9, 5, 0, 0, 0},
									{0, 9, 8, 0, 0, 0, 0, 6, 0},
									{8, 0, 0, 0, 6, 0, 0, 0, 3},
									{4, 0, 0, 8, 0, 3, 0, 0, 1},
									{7, 0, 0, 0, 2, 0, 0, 0, 6},
									{0, 6, 0, 0, 0, 0, 2, 8, 0},
									{0, 0, 0, 4, 1, 9, 0, 0, 5},
									{0, 0, 0, 0, 8, 0, 0, 7, 9}
									};


bool is_valid(int row, int col, int num);
bool solve();
void print_board();


int main(int argc, char const *argv[])
{
	
	print_board();
	printf("\nsolving...\n\n");
	solve();

	print_board();
	return 0;
}


bool is_valid(int row, int col, int num)
{
	for (int i = 0; i<BOARD_SIZE; i++)
		if (board[row][i] == num || board[i][col] == num)
			return false;

	int square_row = (row / 3);
	int square_col = (col / 3);

	for (int i = 0; i<3; i++)
		for (int j = 0; j<3; j++)
			if (board[square_row * 3 + i][square_col * 3 + j] == num)
				return false;

	return true;
}

bool solve()
{
	for (int i = 0; i < BOARD_SIZE; i++)
	{
		for (int j =  0; j < BOARD_SIZE; j++)
		{
			if (board[i][j] != 0)
				continue;

			for (int k = 1; k <= 9; k++)
			{
				if (!is_valid(i, j, k))
					continue;

				board[i][j] = k;
				if (solve())
					return true;
				board[i][j] = 0;
			}
			return false; // Couldn't find a possible number - this board isn't solvable 
		}
	}

	return true; // All squares are filled, and the board is solved
}



void print_board()
{  
	for(int i = 0; i < BOARD_SIZE; i++)
	{
		printf("%i   ", i+1);
		for(int j = 0; j < BOARD_SIZE; j++)
		{
			if (board[i][j] != 0)
				printf("%i", board[i][j]);
			else
				printf(" ");
			if (j < BOARD_SIZE - 1)
				printf("|");
		}
		printf("\n");
	}
}