
from chess_square import Square

def IS_EQ(v, comp) :
  assert v == comp

def IS_GREATER(v, comp) :
  assert v > comp

def IS_LOWER(v, comp) :
  assert v < comp

def IS_NOT_IN(v, comp = []):
  try:
    for compval in comp :
      assert v != compval
  except ValueError as ve:
    print(ve)

def run_square_tests():
  sq_0 = Square(0)
  sq_1 = Square(63)
  sq_2 = Square(43)

  try : IS_EQ(sq_0.as_int(), 0)
  except : print("failed on test 0 ")

  try :     IS_LOWER(sq_0.as_int(), 10)
  except : print("failed on test 1 ")

  try : sq_3 = Square(6000)
  except : print("failed on test 2 [THIS TEST IS SUPPOSED TO FAIL!]")

  try :     IS_EQ(sq_1.as_uint64(), 9223372036854775808)
  except : print("failed on test 3 ")

  try :     IS_EQ(sq_2.as_uint64(), 8796093022208)
  except : print("failed on test 4 ")

  sq_3 = Square(22)
  try :
    IS_EQ(str(sq_3) , 'g3')
  except : print('failed on test 5, output : {}, compare : {}'.format(str(sq_3), 'g3'))

  sq_4 = Square(33) #b5, mirrored g4 == 30

  try :
    IS_EQ(sq_4.as_int() , 33)
  except: print('failed on test 6')
  try:
    IS_EQ(sq_4.as_uint64(), 8589934592)
  except:
    print('failed on test 7')
  try:
    IS_EQ(str(sq_4) , 'b5')
  except: print('failed on test 8')

  sq_4.mirror()

  try:
    IS_EQ(sq_4.as_int(), 30)
  except:
    print('failed on test 9')
  try:
    IS_EQ(sq_4.as_uint64(), 1073741824)
  except:
    print('failed on test 10')
  try:
    IS_EQ(str(sq_4), 'g4')
  except:
    print('failed on test 11')

  sq_5 = Square(0)

  try:
    IS_EQ(sq_5.row, 0)
  except:
    print('failed on test 12')

  try:
    IS_EQ(sq_5.col, 0)
  except:
    print('failed on test 13')

  sq_6 = Square(37)

  try:
    IS_EQ(sq_6.row, 4)
  except:
    print('failed on test 14')

  try:
    IS_EQ(sq_6.col, 5)
  except:
    print('failed on test 15, input: {}, expected : {}'.format(sq_6.col, 5))

  sq_7 = Square(63)

  try:
    IS_EQ(sq_7.row, 7)
  except:
    print('failed on test 16')

  try:
    IS_EQ(sq_7.col, 7)
  except:
    print('failed on test 17, input: {}, expected : {}'.format(sq_7.col, 7))

















