#ifndef GXX_SERIALIZE_H
#define GXX_SERIALIZE_H

#include <gxx/buffer.h>
#include <inttypes.h>

namespace gxx {
	namespace serialize {
		class binary_saver {
			char* strt;
			char* ptr;
			char* end;

		public:
			binary_saver(gxx::buffer buf) {
				dprln(buf.size());
				strt = buf.data();
				ptr = buf.data();
				end = buf.data() + buf.size();
				dprptrln(strt);
				dprptrln(ptr);
				dprptrln(end);
			}

			template<typename T>
			void operator& (T& obj) {
				dump(obj);
			}

			template<typename T>
			void dump(T& obj) {
				obj.template serialize<binary_saver>(*this);
			}

			void dump(short i) {
				dprln("sint");
			}

			void dump(int i) {
				if (ptr + sizeof(int) >= end) return;
				memcpy(ptr, &i, sizeof(int));
				ptr += sizeof(int);
			}

			void dump(long i) {
				dprln("lint");
			}

			void dump(long long i) {
				dprln("llint");
			}

			gxx::buffer getbuf() {
				dprln(ptr - strt);
				return gxx::buffer(strt, ptr - strt);
			}
		};

		class binary_loader {
			char* strt;
			char* ptr;
			char* end;

		public:
			binary_loader(gxx::buffer buf) {
				strt = buf.data();
				ptr = buf.data();
				end = buf.data() + buf.size();
			}

			template<typename T>
			void operator& (T& obj) {
				load(obj);
			}

			template<typename T>
			void load(T& obj) {
				obj.template serialize<binary_loader>(*this);
			}

			//void dump(short i) {
			//	dprln("sint");
			//}

			void load(int& i) {
				if (ptr + sizeof(int) >= end) return;
				memcpy(&i, ptr, sizeof(int));
				ptr += sizeof(int);
			}

			//void dump(long i) {
			//	dprln("lint");
			//}

			//void dump(long long i) {
			//	dprln("llint");
			//}

			//gxx::buffer getbuf() {
			//	dprln(ptr - strt);
			//	return gxx::buffer(strt, ptr - strt);
			//}
		};
	}
}
#endif