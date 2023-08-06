#ifndef GXX_INET2_SOCKET_H
#define GXX_INET2_SOCKET_H

#include <exception>

namespace gxx {
	namespace inet2 {
		struct socket_exception : std::exception {
			int errno;
			const char* what() const {
				return strerror(errno);
			}
		}

		enum class socktype {
			tcp,
			udp,
			unix,
		};

		class socket {
			inet::socket sock;

			//exception
			socket(gxx::hostaddr addr, int port, socktype type);
			socket();
			void connect(gxx::hostaddr addr, int port, socktype type);
			
		};
	}
}

#endif