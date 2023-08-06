#ifndef GXX_IO_FMTPAIRS_H
#define GXX_IO_FMTPAIRS_H

#include <gxx/io/printable.h>
//#include <gxx/argname.h>
#include <gxx/buffer.h>

#include <vector>


namespace gxx {
	namespace io {

		class fmtarg {
		public:
			const printable& ref;
			buffer name; 
		
			fmtarg(const printable& ref) : ref(ref) {}
			fmtarg(const printable& ref, buffer name) : ref(ref), name(name) {}
		};

		class format_arglist {
			std::vector<fmtarg> vec;

		public:
			template<typename ... Args>
			format_arglist(Args&& ... args) : vec { std::forward<Args>(args) ... } {}

			const printable& operator[] (int i) const {
				return vec[i].ref;
			}
		};

		template<typename T>
		fmtarg make_fmtarg(const T& arg) {
			dprln("make_fmtarg(T)");
			return fmtarg();			
		}

		template<typename T>
		fmtarg make_fmtarg(argpair<T>& arg) {
			dprln("make_fmtarg(argpair)");
			return fmtarg(arg.body, arg.name);			
		}

		//template<typename T> auto as_printable(T& obj) { return obj; }

		template<typename ... Args>
		format_arglist __make_format_arglist(Args&& ... args) {
			return format_arglist( fmtarg( as_printable(args) ) ...);
		}

	}
}

#endif
