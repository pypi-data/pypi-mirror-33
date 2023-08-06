#ifndef GXX_FORMAT_WRITER_J
#define GXX_FORMAT_WRITER_J

#include <ostream>
#include <cassert>

#include <gxx/util/numconvert.h>
#include <gxx/util/format.h>
#include <gxx/arglist2.h>

//#include <gxx/io/strm.h>

namespace gxx {
	namespace io {

		enum class CharCase {
			Upper,
			Default,
		};
	
		enum class Alignment {
			Default,
			Left,
			Right,
			Center,
		};
	
		enum class Prefix {
			No,
			Need,
			Bin,
			Oct,
			Hex,
		};
	
		class EmptySpec {
		public:
			Alignment align() const { return Alignment::Default; } 
			CharCase charCase() const { return CharCase::Default; }
			size_t width() const { return 0; }
			char fill() const { return ' '; }
			uint8_t base() const { return 10; }
		};
	
		class AlignSpec : public EmptySpec {
		protected:
			Alignment _align = Alignment::Default; 
			char _fill = ' ';
			size_t _width = 0;
		public:
			AlignSpec() {}
			Alignment align() const { return _align; }
			size_t width() const { return _width; }
			char fill() const { return _fill; }
			AlignSpec& align(Alignment align) { _align = align; ; return *this; }
			AlignSpec& fill(char fill) { _fill = fill; return *this; } 
			AlignSpec& width(size_t width) { _width = width; return *this; } 
		};
	
		class CharStrSpec : public AlignSpec {
		protected:
			CharCase _ccase = CharCase::Default;
		public:
			CharStrSpec() {}
			CharCase charCase() const { return _ccase; }
			CharStrSpec& charCase(CharCase ccase) { _ccase = ccase; return *this; }
			CharStrSpec& align(Alignment align) { _align = align; ; return *this; }
			CharStrSpec& fill(char fill) { _fill = fill; return *this; } 
			CharStrSpec& width(size_t width) { _width = width; return *this; } 
			using AlignSpec::align;
			using AlignSpec::width;
			using AlignSpec::fill; 
		};
	
		class IntegerSpec : public CharStrSpec {
		protected:
			Prefix _prefix = Prefix::No;
			uint8_t _base = 10;
		public:
			IntegerSpec() {}
			Prefix prefix() const { return _prefix; }
			uint8_t base() const { return _base; }
			IntegerSpec& prefix(Prefix prefix) { _prefix = prefix; return *this; }
			IntegerSpec& charCase(CharCase ccase) { _ccase = ccase; return *this; }
			IntegerSpec& align(Alignment align) { _align = align; ; return *this; }
			IntegerSpec& fill(char fill) { _fill = fill; return *this; } 
			IntegerSpec& width(size_t width) { _width = width; return *this; } 
			IntegerSpec& base(uint8_t base) { _base = base; return *this; } 
			using AlignSpec::align;
			using AlignSpec::width;
			using AlignSpec::fill; 
			using CharStrSpec::charCase; 
		};

		class format_writer {
		protected:
			virtual void writeData(const char* str, size_t sz) = 0;
		
		private:
			int format_argument(const char*& fmt, const gxx::visitable_arglist& list, uint8_t& argnum) {
				int ret;
		
				assert(*fmt++ == '{');
		
				const visitable_argument* varg = nullptr;
				
		
				if (isalpha(*fmt)) {
					const char* count_ptr = fmt;
					int len = 0;
					while(isalpha(*count_ptr++)) len++;
					varg = &list[gxx::buffer(fmt, len)];
				} else if (isdigit(*fmt)) {
					varg = &list[atou32(fmt, 10)];
				} else {
					varg = &list[argnum];
				}
		
				while(*fmt != '}' && *fmt != ':' && *fmt != 0) fmt++;
				switch(*fmt) {
					case '}': 
						ret = format_visitor::visit(*varg, *this, nullptr);
						break;
					case ':': 
						ret = format_visitor::visit(*varg, *this, ++fmt);
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

		public:
			void print_impl(const char* fmt, const gxx::visitable_arglist& list) {
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

		public:
			void write(const char* dat, size_t sz) {
				writeData(dat, sz);
			}

			template<typename ... Args>
			void print(const char* fmt, Args&& ... args) {
				print_impl(fmt, make_visitable_arglist<format_visitor>(std::forward<Args>(args) ...));	
			}	

			void print(const char* str) {
				writeData(str, strlen(str));
			}

			void print(int64_t i64) {
				write_int_spec(i64, IntegerSpec());
			}

			void print(std::string str) {
				writeData(str.data(), str.size());
			}

			template<typename ... Args>
			void println(Args ... args) {
				print(std::forward<Args>(args) ...);
				writeData("\r\n", 2);
			}			

			int putchar(char c) {
				writeData(&c,1);
			}

			/*template<typename Spec>
			int write_str_spec(const gxx::string& str, const Spec& spec = EmptySpec()) const {
				return write(str.data(), str.size(), spec);
			}*/
	
			int write_fill(char c, int n) {
				int res = 0;
				while (n--) {
					res += putchar(c); 
				}	
				return res;
			}
	
			template<typename Spec = EmptySpec>
			int write_spec(const char* str, size_t len, const Spec& spec) {
				int ret = 0;
	
				int prewidth = 0;
				int postwidth = 0;
	
				if (spec.width() > len) {
					size_t tofill = spec.width() - len;
					switch(spec.align()) {
						case Alignment::Default:
						case Alignment::Right: 	
							prewidth = tofill; 
							break;
						case Alignment::Left: 	
							postwidth = tofill; 
							break;
						case Alignment::Center: 
							prewidth = tofill / 2  + tofill % 2; 
							postwidth = tofill / 2; 
							break;
					}
				}
	
				if (prewidth) ret += write_fill(spec.fill(), prewidth);
	
				switch (spec.charCase()) {
					case CharCase::Default:
						writeData(str, len);
						ret += len;
						break;
					case CharCase::Upper:
						while(len--) {
							ret += putchar(toupper(*str++));
						}			
						break;
				}
	
				if (postwidth) ret += write_fill(spec.fill(), postwidth);
	
				return ret; 
			}
	/*
			template<typename Spec = EmptySpec>
			int write_cstr(const char* str, const Spec& spec = Spec()) const {
				return write(str, strlen(str), spec);
			}
	*/
			template<typename Spec = IntegerSpec>
			int write_int_spec(int64_t num, const IntegerSpec& spec) {
				int ret = 0;
				char str[100];
				
				switch (spec.prefix()) {
					case Prefix::Bin: ret += putchar('0'); ret += putchar('b'); break;
					case Prefix::Hex: ret += putchar('0'); ret += putchar('x'); break;
					case Prefix::Oct: ret += putchar('0'); break;
					default: break;
				}
	
				i64toa(num, str, spec.base()); 
				ret += write_spec(str, strlen(str), spec);
				return ret;
			}


			/*int write_int(int64_t num) const {
				char str[100];
				i64toa(num, str, 10); 
				return write(str, strlen(str));
			}*/
		};

		class format_ostream_writer : public format_writer {
			std::ostream& out;

		public:
			format_ostream_writer(std::ostream& out) : out(out) {};	

			void writeData(const char* data, size_t size) override {
				out.write(data, size);
			}					
		};

		class strmout;
		class format_gxx_strmout_writer : public format_writer {
			gxx::io::strmout& out;

		public:
			format_gxx_strmout_writer(gxx::io::strmout& out) : out(out) {};	

			void writeData(const char* data, size_t size) override;

			/*void writeData(const char* data, size_t size) override {
				out.write(data, size);
			}	*/				
		};
	}
}

#endif