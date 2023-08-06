#ifndef GXX_TEXT_READER_H
#define GXX_TEXT_READER_H

#include <gxx/io/reader.h>
#include <gxx/utility.h>
#include <gxx/string.h>
#include <ctype.h>

namespace gxx {
	class text_reader : public reader {
	public:
		text_reader(istream& is) : reader(is) {};

		int ignore() const { return is.ignore(); }
		int ignore(int i) const { return is.ignore(i); }

		int ignore_until(char c) const { 
			char p;
			int ret = 0;
			while(1) {
				p = is.peek();
				if (p == 0 || p == c) return ret;
				ret += is.ignore();
			} 
			//return ret;
		}

		template<typename Functor>
		int ignore_until(Functor&& func) const {
			return is.ignore_until(std::forward<Functor>(func));
		}

		template<typename Functor>
		int ignore_while(Functor&& func) const {
			return is.ignore_while(std::forward<Functor>(func));
		}

		int read_int_decimal() const {
			int64_t num = 0;
			char c;
			while(isdigit(c = is.peek())) {
				num *= 10;
				num += c - '0';
				is.ignore();
			} 
			return num;
		}

		gxx::string read_string_until(char c, int maxlen = 64) const {
			gxx::string str;
			str.reserve(maxlen);
			int len = is.read_until(str.data(), str.capacity(), c);
			str.set_size(len);
			return str;
		}

		template <typename Functor>
		gxx::string read_string_while(Functor func, int mblen = 64) const {
			gxx::string str;
			str.reserve(mblen);
			
			char c;
			while(func(c = is.peek())) {
				str.concat(is.getchar());
			}

			return str;
		}

		/*int ignore_spaces() const {
			debug_putchar(peek());
			while(1) {
				char c = is.peek();
				if ( c == ' ' || c =='\n' || c =='\r' || c == '\t') is.ignore();
				else { 
					return 99;
				}
			}
		}*/
	};
}

#endif