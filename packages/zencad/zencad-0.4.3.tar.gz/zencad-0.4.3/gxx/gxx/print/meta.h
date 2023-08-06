#ifndef GXX_UTIL_PRINT_H
#define GXX_UTIL_PRINT_H

//Функции печати задаются с помощью специализации шаблонов структур для того, чтобы их можно было
//подтягивать по всей программе.  
#include <gxx/io/ostream.h>
#include <gxx/util/booltype.h>

namespace gxx {
	template <typename T, typename U = int>
	struct is_have_fmtPrintTo : gxx::false_type { };

	template <typename T>
	struct is_have_fmtPrintTo <T, decltype((void) &T::fmtPrintTo, 0)> : gxx::true_type { };

	template <typename T, typename U = int>
	struct is_have_printTo : gxx::false_type { };

	template <typename T>
	struct is_have_printTo <T, decltype((void) &T::printTo, 0)> : gxx::true_type { };

	namespace io { class ostream; }

	template<typename T, bool HavePrintTo = true>
	struct print_functions_basic {
		static int print(gxx::io::ostream& o, const T& obj) {
			return obj.printTo(o);
		}
	};

	template<typename T>
	struct print_functions_basic<T, false> {
		static int print(gxx::io::ostream& o, const T& obj) {
			return o.print(obj);
		};
	};

	template<typename T>
	struct print_functions : public print_functions_basic<T, is_have_printTo<T>::value> {};

	template<typename T, bool Printable = true>
	struct fprint_functions_basic {
		static int format_print(const T& obj, gxx::io::ostream& o, gxx::buffer opt) {
			return obj.fmtPrintTo(o, opt);
		};
	};

	template<typename T>
	struct fprint_functions_basic<T, false> {
		static int format_print(const T& obj, gxx::io::ostream& o, gxx::buffer opt) {
			return print_functions<T>::print(o, obj);
		}
	};

	template<typename T>
	struct fprint_functions : public fprint_functions_basic<T, is_have_fmtPrintTo<T>::value> {};

	template<typename T>
	struct fprint_functions<T*> {
		static int format_print(const T* const obj, gxx::io::ostream& o, gxx::buffer opt) {
			return print_functions<const T*>::print(o, obj);
		}
	};
}

#endif
