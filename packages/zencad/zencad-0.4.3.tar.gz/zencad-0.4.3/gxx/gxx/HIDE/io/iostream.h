#ifndef GXX_IOSTREAM_H
#define GXX_IOSTREAM_H

#include <stdlib.h>
#include <string.h>

namespace gxx {
	
	class istream {
	public:
		virtual int read(char* str, size_t sz) = 0;
		virtual int read_until(char* str, size_t max, char c) {
			int ret = 0;
			char p;
			while((p = peek()) != c && max--) {
				*str++ = p;
				ignore();
				ret++;
			}
			return ret;
		}
		
		virtual int getchar() = 0;
		virtual int peek() = 0;
		
		virtual int ignore(int i) {
			int ret = 0;
			while(i--) {
				if (getchar() == -1) return ret;
				ret++;
			}
			return ret;
		};

		virtual int ignore() {
			//dpr("ign("); dprhex(peek()); dpr(")("); debug_putchar(peek());dpr(")");
			char c = getchar();
			return c == -1 ? -1 : 1;
		};

		template<typename Functor>
		int ignore_until(Functor&& func) {
			int ret = 0;
			while(!func(peek)) {
				if (ignore() == -1) return ret; 
				ret++;
			}
			return ret;
		}

		template<typename Functor>
		int ignore_while(Functor&& func) {
			int ret = 0;
			while(func(peek())) {
				if (ignore() == -1) return ret; 
				ret++;
			}
			return ret;
		}
	};
	
	class ostream {
	public:
		virtual int write(const char* str, size_t sz) = 0;
		virtual int putchar(char c) = 0;

		int print(const char* str) {
			return write(str, strlen(str));
		}
	};
	
	class iostream : public istream, public ostream {};
	
	class debug_ostream : public ostream {
	public:
		int write(const char* str, size_t sz) override {
			debug_write(str, sz);
			return -1;
		}
		
		int putchar(const char c) override {
			debug_putchar(c);
			return -1;
		}
	};

}

#endif