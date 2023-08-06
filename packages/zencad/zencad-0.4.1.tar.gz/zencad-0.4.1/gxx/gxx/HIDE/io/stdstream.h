#ifndef GXX_STDSTREAM_H
#define GXX_STDSTREAM_H

#include <gxx/io/iostream.h>
#include <unistd.h>
#include <iostream>
#include <fstream>

namespace gxx {

	class std_stream : public gxx::iostream {
	public:
		virtual int read(char* str, size_t sz) {
			return std::cin.read(str, sz).gcount();
		}

		virtual int getchar() {
			char c;
			std::cin >> c;
			return c;
		}

		virtual int peek() {
			return std::cin.peek();
		}

		virtual int write(const char* str, size_t sz) {
			std::cout.write(str, sz);
			return sz;
		}

		virtual int putchar(char c) {
			std::cout << c;
			return 1;
		}

	};

	class std_fstream : public gxx::iostream {
	public:
		const char* path;
		std::fstream strm;
		std_fstream(const char* path) : strm(path) {}

		virtual int read(char* str, size_t sz) {
			return strm.read(str, sz).gcount();
		}

		virtual int getchar() {
			return strm.get();
		}

		virtual int peek() {
			return strm.peek();
		}

		virtual int write(const char* str, size_t sz) {
			strm.write(str, sz);
			return sz;
		}

		virtual int putchar(char c) {
			strm << c;
			return 1;
		}

	};
}

#endif