#ifndef GXX_SSTREAM_H
#define GXX_SSTREAM_H

#include <iostream>
#include <gxx/io/iostream.h>

namespace gxx {
	namespace io {
		class std_string_writer : public gxx::io::ostream {
			std::string& str;
		public:
			std_string_writer(std::string& _str) : str(_str) {}
		protected:
			virtual int writeData(const char* ptr, size_t sz) {
				str.append(ptr, sz);
				return sz;
			}
		};

		class std_ostream_writer : public gxx::io::ostream {
			std::ostream& out;
		public:
			std_ostream_writer(std::ostream& _out) : out(_out) {}
		protected:
			virtual int writeData(const char* ptr, size_t sz) {
				out.write(ptr, sz);
				return sz;
			}
		};

		class std_ostream : public gxx::io::ostream {
		private:
			std::ostream& out;

		public:
			std_ostream(std::ostream& o) : out(o) {}
			int writeData(const char* ptr, size_t sz) override {
				out.write(ptr, sz);
				return sz;
			}
		};

		class std_istream : public gxx::io::istream {
		private:
			std::istream& in;

		public:
			std_istream(std::istream& i) : in(in) {}
			int readData(char* ptr, size_t sz) override {

				gxx::println("here7");
				in.read(ptr, sz);

				gxx::println("here8");
				return in.gcount();
			}
		};


		//std_ostream cout(std::cout.rdbuf());
		extern std_ostream cout;
		//extern std_ostream cerr;
		extern std_istream cin;
	}
}

#endif
