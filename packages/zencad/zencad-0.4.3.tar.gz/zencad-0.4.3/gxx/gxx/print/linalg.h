#ifndef GXX_PRINT_LINALG_H
#define GXX_PRINT_LINALG_H

#include <gxx/print.h>
#include <gxx/math/linalg.h>

namespace gxx {

	template<class T, int M, int N>
	struct print_functions<linalg::mat<T,M,N>> {
		static int print(gxx::io::ostream& o, const linalg::mat<T,M,N>& m) {
			int ret = 0;
			for (int i = 0; i < N - 1; ++i) {
				ret += gxx::println(m.row(i));
			}
			ret += gxx::print(m.row(N-1)); 
			return ret;
		}		
	};

	template<class T, int M>
	struct print_functions<linalg::vec<T,M>> {
		static int print(gxx::io::ostream& o, const linalg::vec<T,M>& v) {
			int ret = 0;
			for (int i = 0; i < M; ++i) {
				ret += gxx::print(v[i]);
				ret += gxx::putchar(' ');
			}
			return ret;
		}		
	};

}

#endif