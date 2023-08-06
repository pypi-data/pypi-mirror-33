#ifndef GXX_ARRAY_PRINT_H
#define GXX_ARRAY_PRINT_H

#include <gxx/print.h>

//Классы, определяющие печатающие методы для типовых структур данных.
namespace gxx {
	template<typename T>
	class array_printable {
	public:
		size_t printTo(gxx::io::ostream& o) const {
			const auto& self = *reinterpret_cast<const T*>(this);
			o.putchar('[');
			for (int i = 0; i < self.size(); ++i) {
				gxx::print(self[i]);
				if (i != self.size() - 1) o.putchar(' ');
			}
			o.putchar(']');
		}
	};

	template<typename T>
	class matrix_printable {
	public:
		size_t printTo(gxx::io::ostream& o) const {
			const auto& self = *reinterpret_cast<const T*>(this);
			for (int i = 0; i < self.size1(); ++i) {
				for (int j = 0; j < self.size2(); ++j) {
					gxx::print(self(i,j));
					o.putchar(' ');
				}
				o.println();
			}
		}
	};
}
#endif