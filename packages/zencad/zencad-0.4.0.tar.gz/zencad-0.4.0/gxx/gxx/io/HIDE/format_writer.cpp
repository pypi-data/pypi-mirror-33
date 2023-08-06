#include <cassert>

#include <gxx/util/format.h>
#include <gxx/arglist.h>

#include <gxx/io/format_writer.h>

namespace gxx {
	namespace io {
		int format_writer::format_argument(const char*& fmt, const gxx::arglist& list, uint8_t& argnum) {
			int ret;
	
			assert(*fmt++ == '{');
	
			if (isdigit(*fmt)) {
				argnum = atou32(fmt, 10);
			} 
	
			if (isalpha(*fmt)) {
				const char* count_ptr = fmt;
				int len = 0;
				while(isalpha(*count_ptr++)) len++;
				argnum = list.find_name(fmt,len);
				if (argnum == 0xFF) {
					dprln("name error");
					abort();
				}
			} 
	
			while(*fmt != '}' && *fmt != ':' && *fmt != 0) fmt++;
			switch(*fmt) {
				case '}': 
					ret = format_visitor::visit(list[argnum], *this, nullptr);
					break;
				case ':': 
					ret = format_visitor::visit(list[argnum], *this, ++fmt);
					break;
				case 0	: 
					return -1;
				default: 
					dprln("format internal error");
					abort();
			}
			while(*fmt != '}' && *fmt != 0) fmt++;
			fmt++;
			return ret;
		}
		
		void format_writer::print_impl(const char* fmt, const gxx::arglist& list) {
			uint8_t argnum = 0;
			const char* fmtptr = fmt;
		
			while(*fmtptr != 0) {
				if (*fmtptr == '{') {
					format_argument(fmtptr, list, argnum);
					argnum++;
				} else {
					auto strttxt = fmtptr;
					while (*fmtptr != 0 && *fmtptr != '{') fmtptr++;
					writeData(strttxt, fmtptr - strttxt);
				}
			}
		}
		
		void format_writer::write(const char* dat, size_t sz) {
			writeData(dat, sz);
		}
		void format_writer::print(const char* str) {
			writeData(str, strlen(str));
		}
		void format_writer::print(int64_t i64) {
			write_int_spec(i64, IntegerSpec());
		}
		void format_writer::print(std::string str) {
			writeData(str.data(), str.size());
		}
		int format_writer::putchar(char c) {
			writeData(&c,1);
		}
		/*template<typename Spec>
		int write_str_spec(const gxx::string& str, const Spec& spec = EmptySpec()) const {
			return write(str.data(), str.size(), spec);
		}*/

		int format_writer::write_fill(char c, int n) {
			int res = 0;
			while (n--) {
				res += putchar(c); 
			}	
			return res;
		}

	}
}
