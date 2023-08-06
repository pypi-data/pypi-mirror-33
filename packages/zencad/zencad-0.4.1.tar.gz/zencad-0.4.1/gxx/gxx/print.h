#ifndef GXX_PRINT_H
#define GXX_PRINT_H

#include <gxx/print/meta.h>
#include <gxx/print/format.h>
#include <gxx/io/ostream.h>
#include <gxx/io/stdstream.h>
#include <gxx/arglist.h>


namespace gxx {
	extern gxx::io::ostream* standart_output;

	static inline int putchar(gxx::io::ostream& out, char c) {
		return out.putchar(c);	
	}

	static inline int putchar(char c) {
		return standart_output->putchar(c);	
	}

	static inline int write_to(gxx::io::ostream& out, const char* buf, size_t sz) {
		return out.write(buf, sz);
	}

	static inline int write(const char* buf, size_t sz) {
		return gxx::write_to(*standart_output, buf, sz);
	}

	static inline int writeln_to(gxx::io::ostream& out, const char* buf, size_t sz) {
		int ret;
		ret += out.write(buf, sz);
		ret += out.println();
		return ret;
	}

	static inline int writeln(const char* buf, size_t sz) {
		return gxx::writeln_to(*standart_output, buf, sz);
	}

	template<typename Arg>
	int print_to(gxx::io::ostream& out, const Arg& arg) {
		int res = 0;
		res += gxx::print_functions<Arg>::print(out, arg);
		return res;
	}

	template<typename Head, typename ... Tail>
	int print_to(gxx::io::ostream& out, const Head& head, const Tail& ... tail) {
		int res = 0;
		res += print_to(out, head);
		res += out.putchar(' ');
		res += print_to(out, tail ...);
		return res;
	}

	template<typename ... Args>
	int println_to(gxx::io::ostream& out, const Args& ... args) {
		int res = 0;
		res += print_to(out, args ...);
		res += out.println();
		return res;
	}

	template<typename Arg>
	int print(const Arg& arg) {
		return gxx::print_to(*standart_output, arg);
	}

	template<typename Head, typename ... Tail>
	int print(const Head& head, const Tail& ... tail) {
		int res = 0;
		res += print(head);
		res += standart_output->putchar(' ');
		res += print(tail ...);
		return res;
	}

	template<typename ... Args>
	int println(const Args& ... args) {
		int res = 0;
		res += print(args ...);
		res += standart_output->println();
		return res;
	}

	inline int println() {
		return standart_output->println();
	}

	template<typename C>
	int print_as_matrix(const C& c, int rlen) {
		int n = 0;
		int res = 0;
		for (const auto& v : c) {
			res += standart_output->print(v);
			res += standart_output->putchar(' ');
			++n;
			if (n == rlen) {
				n = 0;
				res += standart_output->println();
			}
		}
		return res;
	}

	inline int fprint_format_argument(gxx::io::ostream& out, const char*& fmt, const gxx::visitable_arglist& list, uint8_t argnum) {
		int ret;
		char* pend;
		assert(*fmt++ == '{');

		const visitable_argument* varg = nullptr;

		if (isalpha(*fmt)) {
			const char* count_ptr = fmt;
			int len = 0;
			while(isalpha(*count_ptr++)) len++;
			varg = &list[gxx::buffer(fmt, len)];
		} else if (isdigit(*fmt)) {
			varg = &list[atou32(fmt, 10, &pend)];
		} else {
			varg = &list[argnum];
		}

		while(*fmt != '}' && *fmt != ':' && *fmt != 0) fmt++;
		switch(*fmt) {
			case '}':
				ret = gxx::fmt::format_visitor::visit(*varg, out, gxx::buffer());
				break;
			case ':':
				++fmt;
				ret = gxx::fmt::format_visitor::visit(*varg, out, gxx::buffer(fmt, strchr(fmt, '}') - fmt));
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

	inline int fprint_impl(gxx::io::ostream& out, const char* fmt, const visitable_arglist& args) {
		uint8_t argnum = 0;
		const char* fmtptr = fmt;
		size_t ret = 0;

		while(*fmtptr != 0) {
			if (*fmtptr == '{') {
				ret += fprint_format_argument(out, fmtptr, args, argnum);
				argnum++;
			} else {
				auto strttxt = fmtptr;
				while (*fmtptr != 0 && *fmtptr != '{') fmtptr++;
				ret += out.write(strttxt, fmtptr - strttxt);
			}
		}
		return ret;
	}

	template<typename ... Args>
	int fprint_to(gxx::io::ostream& out, const char* fmt, Args&& ... args) {
		visitable_argument buffer[sizeof ... (Args)];
		return fprint_impl(out, fmt, gxx::make_visitable_arglist<gxx::fmt::format_visitor>(buffer, std::forward<Args>(args) ...));
	}

	template<typename ... Args>
	int fprint(const char* fmt, Args&& ... args) {
		return gxx::fprint_to(*standart_output, fmt,  std::forward<Args>(args) ...);
	}

	template<typename ... Args>
	int fprintln(Args&& ... args) {
		fprint_to(*standart_output, std::forward<Args>(args) ...);
		return standart_output->println();
	}

	template<typename ... Args>
	int fprintln_to(gxx::io::ostream& out, Args&& ... args) {
		fprint_to(out, std::forward<Args>(args) ...);
		return standart_output->println();
	}

	template<typename ... Args>
	std::string format(const char* fmt, Args&& ... args) {
		std::string str;
		gxx::io::ostringstream writer(str);
		gxx::fprint_to(writer, fmt, std::forward<Args>(args) ...);
		return str;
	}

	template<typename Arg>
	std::string to_string(Arg&& arg) {
		std::string str;
		gxx::io::ostringstream writer(str);
		gxx::print(writer, std::forward<Arg>(arg));
		return str;
	}

	inline void print_dump_to(gxx::io::ostream& out, const void *mem, uint16_t len, int columns = 8) {
		int i, j;

		for(i = 0; i < len + ((len % columns) ? (columns - len % columns) : 0); i++) {
			// print offset
			if(i % columns == 0) {
				out.write("0x",2);
				out.print((void*)((char*)mem + i));
				out.putchar(':');
			}

			// print hex data
			if(i < len) {
				out.printhex(((char*)mem)[i]);
				out.putchar(' ');
			}
			else {
				// end of block, just aligning for ASCII dump
				out.write("   ", 3);
			}

			// print ASCII dump
			if(i % columns == (columns - 1))
			{
				for(j = i - (columns - 1); j <= i; j++) {
					if(j >= len) {
						// end of block, not really printing
						out.putchar(' ');
					}
					else if(isprint(((char*)mem)[j])) {
						// printable char
						out.putchar(0xFF & ((char*)mem)[j]);
					}
					else {
						// other char
						out.putchar('.');
					}
				}
				out.putchar('\n');
			}
		}
	}

	inline void print_dump(const void *mem, uint16_t len, int columns = 8) {
		print_dump_to(*standart_output, mem, len, columns);
	}

	inline void print_dump(const std::string& str, int columns = 8) {
		print_dump_to(*standart_output, str.data(), str.size(), columns);
	}

	inline void printhex(const void* data, size_t size) {
		uint8_t* _data = (uint8_t*) data;
		while(size--) {
			standart_output->putchar(byte2sym(*_data >> 4));
			standart_output->putchar(byte2sym(*_data++ & 0x0F));
		}
	}
}

#define GXX_PRINT(arg) gxx::println(#arg ":", arg)

#endif
