## Introspective CRC
This challenge required some familiarity with matrix math.

### Description
Category: Cryptography  
Difficulty: Easy
```
We saw https://shells.aachen.ccc.de/~spq/md5.gif and were inspired.

Challenge running at selfhash.ctfcompetition.com:1337
```

### Exploration
Let's connect to `selfhash.ctfcompetition.com:1337` and see what happens.
```
notcake@notcake:~/googlectf$ nc selfhash.ctfcompetition.com 1337
Give me some data: aaa

Check failed.
Expected:
    len(data) == 82
Was:
    3
notcake@notcake:~/googlectf$ echo "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" | nc selfhash.ctfcompetition.com 1337
Give me some data:
Check failed.
Expected:
    set(data) <= set("01")
Was:
    set(['a'])
notcake@notcake:~/googlectf$ echo "0000000000000000000000000000000000000000000000000000000000000000000000000000000000" | nc selfhash.ctfcompetition.com 1337
Give me some data:
Check failed.
Expected:
    crc_82_darc(data) == int(data, 2)
Was:
    1021102219365466010738322L
    0
```
At this point we know the challenge wants an 82-bit binary string whose `crc_82_darc` equals itself, ie. `crc_82_darc(tobinary(x)) == x`, where `x` is an 82-element vector of bits.

A quick google search for `crc_82_darc` yields a Python implementation in pwntools ([pwnlib.util.crc.crc_82_darc](http://docs.pwntools.com/en/stable/util/crc.html#pwnlib.util.crc.crc_82_darc)).

Brute forcing `crc_82_darc(tobinary(x)) == x` is clearly madness and iterating `x' = crc_82_darc(tobinary(x))` to find the fixed point doesn't go anywhere fast (and might not even find the fixed point at all).

Thankfully the CRC function is pretty much [linear](https://en.wikipedia.org/wiki/Linear_system#Definition) (actually affine), and we can solve for `x` with math. You can skip the rest of this writeup if you know how to do this.

### Linearity of CRC
Toggling a given bit in the CRC input always results in the same set of output bits toggled,
ie. in some sense:
```
"00000011" = "00000000" +
             ("00000001" - "00000000") +
             ("00000010" - "00000000")
crc("00000011") = crc("00000000") +
                  (crc("00000001") - crc("00000000")) +
                  (crc("00000010") - crc("00000000"))
```
This works if addition is bitwise `xor`.
Subtraction is also bitwise `xor` since `xor` twice will reverse itself.
These bit operations happen to be the Galois field with 2 elements, [GF(2)](https://en.wikipedia.org/wiki/GF(2)). We can totally do vector and matrix  math over this field, ({ 0, 1 }, xor, and), even though it's not the usual (ℝ, +, ×).

### Linear algebra time
We can represent the equation we want to solve, `crc_82_darc(tobinary(x)) == x` as a massive system of linear equations (Remember that `+` is `xor` and `*` is `and`!).
```
x = crc(tobinary(x))
x = k +
    x[0] * crcdiff("1000...") +
    x[1] * crcdiff("0100...") +
    ...
x = k + D x
```
where `k = crc("000...")`,
`crcdiff(x) = crc(x) - k` and `D` is the 82x82 square matrix with `crcdiff`s as columns.

Jiggling the equation around to get it into the standard `A x = b` form:
```
k + D x = x
k + D x = I x
k + D x - I x = 0
k + (D - I) x = 0
(D - I) x = -k
```
`I` is shorthand for the 82x82 identity matrix
`0` is shorthand for the 82-bit vector of all `0`s.

Subtraction is the same as addition when it's `xor`, so:
```
(D + I) x = k
```
or `A x = b` where `A = D + I` and `b = k`.

### Retrieving k and D
Remember that `k = crc("000...")`,
`crcdiff(x) = crc(x) - k` and `D` is the 82x82 square matrix with `crcdiff`s as columns.

We can compute `k` and `D` easily with a Python script:

```python
from pwnlib.util.crc import crc_82_darc

def padleft(x):
        return "0" * (82 - len(x)) + x

x0 = '0' * 82
y0 = crc_82_darc(x0)
print("k = [" + ",".join(list(padleft(bin(y0)[2:]))) + "]")

x = x0
for i in range(0, 82):
        x = x0[0:i] + '1' + x0[i + 1:]
        y = crc_82_darc(x)
        dy = y0 ^ y
        print("[" + ",".join(list(padleft(bin(dy)[2:]))) + "]")
```
Now we've got `k` and the columns of `D` and need to invert `D + I`.

### Matrix inversion
Pick your favorite method of solving `A x = b` and run with it!  
I went with [Gaussian elimination](https://en.wikipedia.org/wiki/Gaussian_elimination) which runs in O(n<sup>3</sup>) time. You can skip the rest of this section if you're familiar with this.

Remember that `A = D + I` and `b = k`.

We can turn `A` into an identity matrix, `I`, by adding and subtracting its rows from each other (rows may need to be scaled for real numbers). Adding, subtracting and scaling rows can be represented by a linear operation `B`, ie. another matrix. This is basically turning `A` into [reduced row-echelon form](https://en.wikipedia.org/wiki/Row_echelon_form#Reduced_row_echelon_form).  
Since this linear operation turns `A` into `I`, ie. `B A = I`, `B` must be the inverse of `A`. While doing row addition, subtraction and scaling on `A`, doing the same thing with the corresponding rows of a matrix `I` will produce `B I`, ie. `B`, the inverse.

```lua
-- Best ran with LuaJIT.
function matrix.inv (self)
	local left  = matrix.clone (self)
	local right = matrix.identity (self.h, self.w)
	local success = true
	for y = 0, self.h - 1 do
		-- at this point, for rows y+ of left,
		--   columns 0 to y - 1 are now 0
		-- and we want the diagonal element, left[y][y] = 1
		if left [y * left.w + y] == field.additive_identity then
			-- diagonal element is 0
			-- find row with non-zero element to add in
			-- if there is no such row the matrix is not invertible
			for y1 = y + 1, self.h - 1 do
				if left [y1 * left.w + y] ~= field.additive_identity then
					addRow (left,  y, left,  y1)
					addRow (right, y, right, y1)
					break
				end
			end
		end

		if left [y * left.w + y] ~= field.additive_identity then
			-- row y should now be [ 0 0 ... a ... ], where a != 0
			-- scale it so that a becomes 1
			local k = field.inv (left [y * left.w + y])
			if k ~= field.multiplicative_identity then
				mulRow (left,  y, k)
				mulRow (right, y, k)
			end

			-- row y should now be [ 0 0 ... 1 ... ]
			-- use it to clear that leftmost 1 from all other rows
			for y1 = 0, self.h - 1 do
				if y1 ~= y then
					local k = field.neg (left [y1 * left.w + y])
					if k ~= field.additive_identity then
						mulAddRow (left,  y1, left,  y, k)
						mulAddRow (right, y1, right, y, k)
					end
				end
			end
		else
			-- matrix is non-invertible
			-- but try to process the rest of the columns of the matrix anyway
			success = false
		end
	end
	
	return right, success
end
```

### Solution 1
One of the columns of `A` couldn't be identity-matrix-ized with Gaussian elimination. This means that there's no unique solution to `A x = b` - there could be 0 or 2 or more solutions. [LU decomposition](https://en.wikipedia.org/wiki/LU_decomposition#Solving_linear_equations) might have been more appropriate to use here. In our case there are multiple solutions.

Taking the almost-inverse matrix and multiplying `k` with it produces an `x` of `1010010010111000110111101011101001101011011000010000100001011100101001001100000000`.  
Running it through `crc_82_darc` by hand produces... itself (as hoped). Success!

And the flag:
```
notcake@notcake:~/googlectf$ echo 1010010010111000110111101011101001101011011000010000100001011100101001001100000000 | nc selfhash.ctfcompetition.com 1337
Give me some data:
CTF{i-hope-you-like-linear-algebra}
```

### Solution 2
The 81st column of `A` couldn't be identity-matrix-ized and was `0101100101000011111001100101000001100001110001110111110001111100111010100111100000`. This gives us a solution to `A x = 0` which we can overlay on our previous solution!  
The null space of `A` (ie. solutions to `A x = 0`) is `0101100101000011111001100101000001100001110001110111110001111100111010100111100010` (note the 81st bit set!).

And our alternative solution is  
`1010010010111000110111101011101001101011011000010000100001011100101001001100000000` ^  
`0101100101000011111001100101000001100001110001110111110001111100111010100111100010`  
which gives:  
`1111110111111011001110001110101000001010101001100111010000100000010011101011100010`

And it works as well:
```
notcake@notcake:~/googlectf$ echo 1111110111111011001110001110101000001010101001100111010000100000010011101011100010 | nc selfhash.ctfcompetition.com 1337
Give me some data:
CTF{i-hope-you-like-linear-algebra}
```
