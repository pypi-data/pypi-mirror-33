#ifndef GXX_IO_OSTREAM_H
#define GXX_IO_OSTREAM_H

#include <stdlib.h>
#include <string.h>
#include <gxx/buffer.h>
#include <gxx/util/numconvert.h>
#include <gxx/util/asciiconvert.h>

#include <gxx/debug/dprint.h>

//#include <utility>

namespace gxx {
	namespace io {
		class printable;

		class ostream {
		public:
			virtual int write(const char* str, size_t sz) {
				return writeData(str, sz);
			}

			virtual int putchar(char c) {
				return writeData(&c,1);
			}

			int fill(char c, size_t len) {
				while(len--) {
					putchar(c);
				}
				return len;
			}

			int printhex(char c) {
				putchar(byte2sym((c & 0xF0) >> 4));
				putchar(byte2sym(c & 0x0F));
				return 2;
			}

			int print_hexdata(char* data, size_t size) {
				size_t sz = size;
				while(sz--) {
					printhex(*data++);
				}
				return size << 1;
			}

			template<typename T>
			int printhex(T c) {
				return print_hexdata((char*)&c, sizeof(c));
			}

			int print(bool obj) {
				return print(obj ? "true" : "false");
			}

			int print(const short i) { return print((long long) i); }
			int print(const int i) { return print((long long) i); }
			int print(const long i) { return print((long long) i); }
			int print(const long long i) {
				char buf[48];
				i64toa(i, buf, 10);
				return print(buf);
			}

			int print(const unsigned short i) { return print((unsigned long long) i); }
			int print(const unsigned int i) { return print((unsigned long long) i); }
			int print(const unsigned long i) { return print((unsigned long long) i); }
			int print(const unsigned long long i) {
				char buf[48];
				u64toa(i, buf, 10);
				return print(buf);
			}

			int print(const long double d) {
				char buf[48];
				ftoa(d, buf, 5);
				return print(buf);
			}

			int print(const double d) {
				char buf[48];
				ftoa(d, buf, 5);
				return print(buf);
			}

			int print(const float f) {
				char buf[48];
				ftoa(f, buf, 5);
				return print(buf);
			}

			int print(const char* str) {
				return write(str, strlen(str));
			}

			int print(const void* ptr) {
				char buf[48];
				u64toa((uintptr_t)ptr, buf, 16);
				size_t len = strlen(buf);
				size_t ret = fill('0', sizeof(void*)*2 - len);
				return ret + print(buf);
			}

			int print(gxx::buffer buf) {
				return write(buf.data(), buf.size());
			}

			/*int print(const std::string str) {
				return write(str.data(), str.size());
			}*/

			int print(const gxx::io::printable& obj);

			/*int print(long long i, const fmt::spec_integer& spec) {
				char buf[48];
				i64toa(i, buf, 10);
				return print(buf, spec);
			}

			int print(unsigned long long u, const fmt::spec_integer& spec) {
				return print("print uinteger with spec");
			}

			int print(char str, const fmt::spec_cstring& spec) {
				return print("print char with spec");
			}

			int print(double str, const fmt::spec_float& spec) {
				return print("print double with spec");
			}*/

			template<typename Arg>
			int println(const Arg& arg) {
				int ret = print(arg);
				return ret + write("\r\n", 2);
			}

			int println() {
				return write("\r\n", 2);
			}

			template <typename T>
			int bwrite(T obj) {
				return write((char*)&obj, sizeof(T));
			}

		protected:
			virtual int writeData(const char* str, size_t sz) = 0;
		};

		class printable {
		public:
			virtual size_t printTo(gxx::io::ostream& o) const = 0;
      virtual size_t fmtPrintTo(gxx::io::ostream& o, gxx::buffer opts) const {
				(void) opts;
				return printTo(o);
			}
		};
	}
}

inline int gxx::io::ostream::print(const gxx::io::printable& obj) {
	return obj.printTo(*this);
}

#endif
