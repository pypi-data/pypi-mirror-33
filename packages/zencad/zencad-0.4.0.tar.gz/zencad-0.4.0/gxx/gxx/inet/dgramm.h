#ifndef GXX_DATAGRAMM_SOCKET_H
#define GXX_DATAGRAMM_SOCKET_H

#include <gxx/inet/socket.h>
#include <gxx/print.h>

#include <unistd.h>
#include <fcntl.h>

#ifndef __WIN64__
#	include <netinet/in.h>
#	include <netinet/tcp.h>
#	include <arpa/inet.h>
#endif
//#include <errno.h>

namespace gxx { 
	namespace inet {
		struct datagramm_socket : public inet::socket {
			datagramm_socket(int domain, int type, int proto);
			int sendto(gxx::inet::hostaddr haddr, int port, const char* data, size_t size);
			int ne_sendto(uint32_t addr, uint16_t port, const char* data, size_t size);
			int recvfrom(char* data, size_t maxsize, gxx::inet::netaddr* inaddr);
		};
	
		struct udp_socket : public datagramm_socket {
			udp_socket();
			udp_socket(gxx::inet::hostaddr addr, int port);
			int bind(gxx::inet::hostaddr addr, int port);
		};

		struct rdm_socket : public datagramm_socket {
			rdm_socket();
			rdm_socket(gxx::inet::hostaddr addr, int port);
		};
	}
}

#endif
