#ifndef GXX_FMT_FORMAT_H
#define GXX_FMT_FORMAT_H

#include <gxx/arglist.h>

namespace gxx {
	namespace io { class ostream; }
	namespace fmt {
		//Форматирующий визитёр для arglist.
		struct format_visitor {
			using ftype = size_t(*)(void*, gxx::io::ostream&, gxx::buffer opts);												
		
			template<typename Object>
			static void* get_visit() {
				return reinterpret_cast<void*>(&fprint_functions<Object>::format_print);
			}

			template<typename ... Args>												
			static inline size_t visit(gxx::visitable_argument varg, Args&& ... args) {		
				ftype fptr = (ftype) varg.visit;									
				return fptr(varg.ptr, std::forward<Args>(args) ...);				
			}																		
		};
		
		/*struct spec_text {
			unsigned char width = 0;
			signed char allign = 0;

			spec_text(gxx::buffer buf) {
				char* end = buf.data() + buf.size();
				for (char* ptr = buf.data(); ptr != end; ++ptr) {
					//dprln("here");
					char c = *ptr;
					if (isdigit(c)) {
						char* end;
						width = atou32(ptr, 10, &end);
						while(isdigit(*ptr)) ++ptr; --ptr;
						continue;
					}
					switch(c) {
						case '>': allign = 1; continue; 
					}
				}
			}
		};

		struct spec_cstring : public spec_text {
		public:
			spec_cstring(gxx::buffer buf) : spec_text(buf) {}
		};

		struct spec_integer : public spec_text {
		public:
			spec_integer(gxx::buffer buf) : spec_text(buf) {}
		};

		struct spec_float : public spec_text {
		public:
			spec_float(gxx::buffer buf) : spec_text(buf) {}
		};*/
	}
}


#endif