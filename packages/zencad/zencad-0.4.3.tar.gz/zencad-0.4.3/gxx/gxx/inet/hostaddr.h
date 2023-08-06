#ifndef GXX_INETADDR_H
#define GXX_INETADDR_H

#include <ctype.h>
#include <gxx/print.h>
#include <gxx/util/string.h>

namespace gxx {
	class hostaddr {
	public:
		uint32_t addr;
		hostaddr() : addr(0) {}
		hostaddr(uint32_t addr) : addr(addr) {}
		
		hostaddr(const char* str) {
			if (isdigit(*str)) {
				gxx::strvec nums = gxx::split(str, '.');
				addr =
					atoi(nums[0].c_str()) << 24 |
					atoi(nums[1].c_str()) << 16 |
					atoi(nums[2].c_str()) << 8 |
					atoi(nums[3].c_str());
			}
		}

		hostaddr(const std::string& str) : hostaddr(str.c_str()) {}

		size_t printTo(gxx::io::ostream& o) const {
			return o.printhex(addr);
		}
		
		bool operator == (const hostaddr& oth) const {
			return oth.addr == addr;
		}
	};

	namespace inet {
		static constexpr const char* localhost = "127.0.0.1"; 
		using hostaddr = gxx::hostaddr;

		struct netaddr {
			hostaddr addr;
			int32_t port;
			netaddr(unsigned long addr, unsigned short port) 
				: addr(addr), port(port) {}

			netaddr(gxx::inet::hostaddr addr, unsigned short port) 
				: addr(addr), port(port) {}

			netaddr() = default;
			size_t printTo(gxx::io::ostream& o) const {
				return gxx::fprint_to(o, "(h:{},p:{})", addr, port);
			}

			bool operator==(const netaddr& oth) const {
				return oth.addr == addr && oth.port == port;
			}
		};
	}
}

namespace std {
	template<> 
	class hash<gxx::inet::hostaddr> {
	public:
		size_t operator()(const gxx::inet::hostaddr &s) const {
			return std::hash<int32_t>()(s.addr);
		}
	};

	template<> 
	class hash<gxx::inet::netaddr> {
	public:
		size_t operator()(const gxx::inet::netaddr &s) const {
			size_t h1 = std::hash<gxx::inet::hostaddr>()(s.addr);
			size_t h2 = std::hash<int32_t>()(s.port);
			return h1 ^ ( h2 << 1 );
		}
	};
}

#endif
