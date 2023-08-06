#ifndef GXX_TEXT_WRITER_H
#define GXX_TEXT_WRITER_H

#include <gxx/io/writer.h>

namespace gxx {

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

	class text_writer : public writer {
	public:
		text_writer(const ostream& os) : writer(const_cast<ostream&>(os)) {} 

		template<typename Spec = EmptySpec>
		int write_str(const gxx::string& str, const Spec& spec = EmptySpec()) const {
			return write(str.data(), str.size(), spec);
		}

		int write_fill(char c, int n) const {
			int res = 0;
			while (n--) {
				res += putchar(c); 
			}	
			return res;
		}

		using writer::write;

		template<typename Spec = EmptySpec>
		int write(const char* str, size_t len, const Spec& spec) const {
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
					ret += write(str, len);
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

		template<typename Spec = EmptySpec>
		int write_cstr(const char* str, const Spec& spec = Spec()) const {
			return write(str, strlen(str), spec);
		}

		template<typename Spec = IntegerSpec>
		int write_int(int64_t num, const IntegerSpec& spec) const {
			int ret = 0;
			char str[100];
			
			switch (spec.prefix()) {
				case Prefix::Bin: ret += putchar('0'); ret += putchar('b'); break;
				case Prefix::Hex: ret += putchar('0'); ret += putchar('x'); break;
				case Prefix::Oct: ret += putchar('0'); break;
				default: break;
			}

			i64toa(num, str, spec.base()); 
			ret += write(str, strlen(str), spec);
			return ret;
		}

		int write_int(int64_t num) const {
			char str[100];
			i64toa(num, str, 10); 
			return write(str, strlen(str));
		}
	};
}

#endif