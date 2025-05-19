#include <iostream>
#include <type_traits>

struct Y { char x; char d; };

int main() {
  std::cout << "alignof(Y) = "
            << std::alignment_of<Y>::value << "\n"
            << "sizeof(Y)  = "
            << sizeof(Y)           << "\n";
}
