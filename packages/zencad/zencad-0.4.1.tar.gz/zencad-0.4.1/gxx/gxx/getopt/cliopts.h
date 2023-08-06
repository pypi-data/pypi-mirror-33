#ifndef GXX_CLIOPTS_H
#define GXX_CLIOPTS_H

#include <gxx/result.h>
#include <gxx/print.h>
#include <gxx/util/ctrdtr.h>

#include <string>
#include <vector>

namespace gxx {
	using namespace gxx::result_type;

	class cliopts {
		enum class Type {
			Bool,
			Integer,
			String,
			Option
		};

		struct opt {
			Type type;
			char short_name;
			const char* long_name;

			union {
				bool b;
				int32_t i32;
				std::string str;
			};

		public:
			opt(const char* l, char s, bool def) 		: long_name(l), short_name(s), type(Type::Bool), b(def) {}
			opt(const char* l, char s, int def) 		: long_name(l), short_name(s), type(Type::Integer), i32(def) {}
			opt(const char* l, char s, std::string def) : long_name(l), short_name(s), type(Type::String), str(def) {}
			opt(const char* l, char s) 					: long_name(l), short_name(s), type(Type::Option), b(false) {}

			opt(const opt& other) : long_name(other.long_name), short_name(other.short_name), type(other.type) {
				switch (type) {
					case Type::String: gxx::constructor(&str, other.str); break;
					case Type::Integer: i32 = other.i32; break;
					case Type::Bool: 
					case Type::Option: b = other.b;
				}
			}

			~opt() {
				if (type == Type::String) gxx::destructor(&str);
			}
		};

	public:
		std::vector<opt> opts;
		std::vector<std::string> args;

		void add_bool(const char* l, char s, bool def) { opts.emplace_back(l, s, def); }
		void add_integer(const char* l, char s, int32_t def) { opts.emplace_back(l, s, def); }
		void add_string(const char* l, char s, std::string def) { opts.emplace_back(l, s, def); }
		void add_string(const char* l, char s, const char* def) { opts.emplace_back(l, s, std::string(def)); }
		void add_option(const char* l, char s) { opts.emplace_back(l, s); }

		result<opt*> get_opt(const char* l) {
			for(auto& o : opts) {
				if (!strcmp(o.long_name, l)) {
					return &o;
				}
			}
                        return error(gxx::format("wrong opt name {}", l).c_str());
		}

		result<opt*> get_opt(char c) {
			for(auto& o : opts) {
				if (c == o.short_name) {
					return &o;
				}
			}
                        return error(gxx::format("wrong opt short_name {}", c).c_str());
		}

		result<opt*> get_opt(const char* l, Type type) {
			for(auto& o : opts) {
				if (!strcmp(o.long_name, l)) {
					if (o.type != type) return error("wrong opt type");
					return &o;
				}
			}
                        return error(gxx::format("wrong opt name {}", l).c_str());
		}

		result<std::string> get_string(const char* l) { 
			return tryS(get_opt(l,Type::String))->str; 
		}
		
		result<int32_t> get_integer(const char* l) { 
			return tryS(get_opt(l,Type::Integer))->i32; 
		}

		result<bool> get_bool(const char* l) { 
			return tryS(get_opt(l,Type::Bool))->b; 
		}

		result<bool> get_option(const char* l) { 
			return tryS(get_opt(l,Type::Option))->b; 
		}

		std::vector<std::string> get_args() { 
			return args; 
		}
		
		enum class AutomState {
			WaitValue,
			Normal
		};

		

		result<void> set_value(opt& o, const char* val) {
			if (*val == 0) return error("wrong option syntax");
			switch(o.type) {
				case Type::String: 
					o.str = std::string(val); 
					break;
				case Type::Integer: 
					o.i32 = atoi(val); 
					break;
			}
			return result<void>();
		}

		static int parse_minus(const char* str, AutomState state) {
			if (*str != '-') return 0;
			if (state == AutomState::WaitValue) return -1;
			if (*(str + 1) == 0) return -1;
			if (*(str + 1) == '-') {
				if (*(str + 2) == 0) return -1;
				return 2;
			}
			return 1;
		}

		result<opt*> parse_long_opt(const char* l, AutomState& state) {
			char buf[64];
			char* ptr = buf;
			while(*l != '=' && *l != 0) {
				*ptr++ = *l++;
			}
			*ptr=0;
			opt* o = tryS(get_opt(buf));

			if (*l == '=') {
				if (o->type == Type::Option || o->type == Type::Bool) 
					return error("wrong option syntax");
				set_value(*o, l+1);
				return o;
			} else {
				if (o->type != Type::Option && o->type != Type::Bool) state = AutomState::WaitValue;
				if (o->type == Type::Bool || o->type == Type::Option) o->b = true;
				return o;
			}
		}

		result<void> parse(int argc, char* argv[]) {
			int i;

			auto state = AutomState::Normal;
			opt* curopt;
			//result<opt&> res;

			for(auto it = argv; argc--; it++) {
				switch(parse_minus(*it, state)) {
					case 0: 
						//dprln(0);
						if (state == AutomState::Normal) {
							args.push_back(std::string(*it));
						} else {
							tryS(set_value(*curopt, *it));
							state = AutomState::Normal;
						}
						continue;
					case 1:
						i = 1;
						while(*(*it+i) != 0) {
							curopt = tryS(get_opt(*(*it+i)));
							if (curopt->type != Type::Option && curopt->type != Type::Bool) {
								if (*(*it+i+1) == 0) {
									state = AutomState::WaitValue;
									break;
								}
								tryS(set_value(*curopt, *it+i+1));
								break;
							} else {
								curopt->b = true;
							}
							i++;
						}
						break;
					case 2: 
						curopt = tryS(parse_long_opt(*it+2, state)); 
						break;
					case -1: return error("wrong option syntax");					
				}
			}
			if (state == AutomState::WaitValue) return error("wrong option syntax");
			return result<void>();
		}

		result<void> parse(int strt, int argc, char* argv[]) {
			return parse(argc - strt, argv + strt);
		}
	};
}

#endif
