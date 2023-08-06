//#include <netinet/in.h>
//#include <netinet/tcp.h>
//#include <arpa/inet.h>
#include <errno.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <unistd.h>
#include <fcntl.h>

#include <gxx/inet/socket.h>
#include <gxx/inet/tcp_socket.h>
#include <gxx/inet/tcp_server.h>
#include <gxx/debug.h>

int gxx::inet::socket::blocking(bool en)
{
	unsigned long mode = en ? 0 : 1;
	return (ioctlsocket(fd, FIONBIO, &mode) == 0) ? true : false;
}

int gxx::inet::socket::nodelay(bool en) {
	int on = en;
	int rc = setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, (char *) &on, sizeof(on));
	return rc;
}

int gxx::inet::socket::reusing(bool en) {
	int on = en;
	int rc = setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (char *) &on, sizeof (on));
	return rc;
}

int gxx::inet::socket::init(int domain, int type, int proto) {
	fd = ::socket(domain, type, proto);
	return fd;
}

int gxx::inet::socket::bind(gxx::inet::hostaddr haddr, int port, int family) {
	struct sockaddr_in addr;
	memset(&addr, 0, sizeof(addr));

	addr.sin_family = family;
	addr.sin_addr.s_addr = htonl(haddr.addr);  //INADDR_ANY = 0.0.0.0
	addr.sin_port = htons(port);

	return ::bind(fd, (sockaddr*) &addr, sizeof(struct sockaddr_in));
}

int gxx::inet::socket::listen(int conn) {
	return ::listen(fd, conn);
}

int gxx::inet::socket::connect(gxx::inet::hostaddr haddr, int port, int family) {
	struct sockaddr_in addr;
	memset(&addr, 0, sizeof(addr));

	addr.sin_family = family;
	addr.sin_port = htons(port);
	addr.sin_addr.s_addr = htonl(haddr.addr);

	return ::connect(fd, (struct sockaddr*) &addr, sizeof(addr));
}

int gxx::inet::socket::send(const char* data, size_t size, int flags) {
	return ::send(fd, data, size, flags);
}

int gxx::inet::socket::recv(char* data, size_t size, int flags) {
	return ::recv(fd, data, size, flags);
}

int gxx::inet::socket::close() {
	int ret = ::shutdown(fd, SD_BOTH);
	/*if (ret < 0) {
		m_errstr = strerror(errno);
		return -1;
	}*/

	ret = ::close(fd);
	/*if (ret < 0) {
		m_errstr = strerror(errno);
		return -1;
	}*/

	return ret;
}

gxx::inet::tcp_socket::tcp_socket(gxx::inet::hostaddr addr, int port) : tcp_socket() {
	inet::socket::init(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	connect(addr, port);
}

int gxx::inet::tcp_socket::init() {
	return inet::socket::init(AF_INET, SOCK_STREAM, IPPROTO_TCP);
}

int gxx::inet::tcp_socket::connect(gxx::inet::hostaddr addr, int port) {
	return socket::connect(addr, port, PF_INET);
}

int gxx::inet::tcp_socket::writeData(const char* data, size_t size) {
	return socket::send(data, size, 0);
}

int gxx::inet::tcp_socket::readData(char* data, size_t size) {
	return socket::recv(data, size, 0);
}

gxx::inet::tcp_server::tcp_server(int port) : tcp_server() {
	init(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	bind("0.0.0.0", port, PF_INET);
	inet::socket::listen(10);
}

gxx::inet::tcp_server::tcp_server(gxx::inet::hostaddr addr, int port) : tcp_server() {
	init(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	bind(addr, port, PF_INET);
	inet::socket::listen(10);
}

void gxx::inet::tcp_server::listen(int port, int conn) {
	init(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	bind("0.0.0.0", port, PF_INET);
	inet::socket::listen(conn);
}

gxx::inet::tcp_socket gxx::inet::tcp_server::accept() {
	int c = sizeof(sockaddr_in);
	sockaddr_in caddr;
	memset(&caddr, 0, sizeof(caddr));
	int cfd = ::accept( fd, (sockaddr*)&caddr, (socklen_t*)&c );

	gxx::inet::tcp_socket sock;
	sock.fd = cfd;
	return sock;
}

/*typedef int socklen_t;

namespace gxx {
	void socket::setError(const char* func, int err) {
		SocketError serr;
		switch (err) {
			case EADDRINUSE: serr = SocketError::AllreadyInUse; break;
			case ECONNREFUSED: serr = SocketError::ConnectionRefused; break;
			case EAGAIN: serr = SocketError::Unavailable; break;	
			case EPIPE: serr = SocketError::BrokenPipe; break;
            default:
                gxx::debug("Unknown error {}", err);
                serr = SocketError::UnknownError; break;
		}
		setError(func, serr);
	}

	void socket::setError(const char* func, SocketError err) {
		m_error = err;
		gxx::debug("socket {0}: {}", func, error());			
	}

	int socket::open() {
		switch(m_type) {
            case socket::type::tcp:
          //      dprln("::socket");
                m_fd = ::socket(AF_INET, SOCK_STREAM, 0);
				break;
			default:
                setError("open", SocketError::WrongSocketType);
				return -1;	
		}
		
        //dprln(m_fd);
        //dprln( WSAGetLastError());

		if (m_fd < 0) {
            setError("open", errno);
			return -1;
		}
	
		//m_state = SocketState::Opened;
		return 0;
	}

	int socket::close() {
		if (m_fd >= 0) {
	
			if (!is_disconnected()) {
                                int ret = ::shutdown(m_fd, SD_BOTH);
				
				if (ret < 0) {
					setError("shutdown", errno);
   					m_state = SocketState::Disconnected;	
					return -1;
   				}
   			}	

   			m_state = SocketState::Disconnected;	
		
			int ret = ::close(m_fd);
			if (ret < 0) {
				setError("close", errno);
				return -1;
   			}
   			
   			return 0;
   		}
	}
	
	int socket::connect() {
		if (m_fd < 0) if (open()) return -1;;

		struct sockaddr_in addr;
		memset(&addr, 0, sizeof(addr));

		switch(m_type) {
			case 
                socket::type::tcp: addr.sin_family = AF_INET;
				break;
			default: 
                setError("connect", SocketError::WrongSocketType);
				return -1;
		}

		addr.sin_port = htons(m_port);
   	 	addr.sin_addr.s_addr = htonl(m_addr.addr);

		if (::connect(m_fd, (struct sockaddr*) &addr, sizeof(addr)) < 0) {
			setError("connect", errno);
			return -1;				
		}

		m_state = SocketState::Connected;		
		return 0;			 
	}

	int socket::listen(int con) {
		if (::listen(m_fd, con) < 0) {
   			setError("listen", errno);
			return -1;
		}

		m_state = SocketState::Listening;
		return 0;		
    }

	int socket::bind() {
		struct sockaddr_in addr;
		memset(&addr, 0, sizeof(addr));
		
		addr.sin_port = htons(m_port);
   	 	addr.sin_addr.s_addr = htonl(m_addr.addr);

        switch(m_type) {
            case
                socket::type::tcp: addr.sin_family = AF_INET;
                break;
            default:
                setError("connect", SocketError::WrongSocketType);
                return -1;
        }

		if (::bind(m_fd, (struct sockaddr*) &addr, sizeof(addr)) < 0) {
            setError("bind", WSAGetLastError());
			m_state = SocketState::Disconnected;
			return -1;
		}

		m_state = SocketState::Bound;
		return 0;			 
	}

    int socket::blocking(bool en)
	{
            unsigned long mode = en ? 0 : 1;
            return (ioctlsocket(m_fd, FIONBIO, &mode) == 0) ? true : false;
	}

	int socket::nodelay(bool en) {
		int on = en;
		int rc = setsockopt(m_fd, IPPROTO_TCP, TCP_NODELAY, (char *) &on, sizeof(on));
		return rc;
	}

	int socket::reusing(bool en) {
		int on = en;
		int rc = setsockopt(m_fd, SOL_SOCKET, SO_REUSEADDR, (char *) &on, sizeof (on));
		return rc;
	}

	gxx::socket socket::accept() {
		gxx::socket ret;

		int c = sizeof(sockaddr_in);
		sockaddr_in caddr;
		memset(&caddr, 0, sizeof(caddr));

		int cfd = ::accept( m_fd, (sockaddr*)&caddr, (socklen_t*)&c );
		if (cfd < 0) {
			setError("accept", errno);
			return ret;
		}

		ret.init(m_type, caddr.sin_addr.s_addr, caddr.sin_port);
		ret.m_fd = cfd;
		ret.m_state = SocketState::Connected;
		return std::move(ret);
	}


	int socket::try_accept(gxx::socket& ret) {
		int c = sizeof(sockaddr_in);
		sockaddr_in caddr;
		memset(&caddr, 0, sizeof(caddr));

		int cfd = ::accept( m_fd, (sockaddr*)&caddr, (socklen_t*)&c );
		if (cfd < 0) {
			return errno;
		}

		ret.init(m_type, caddr.sin_addr.s_addr, caddr.sin_port);
		ret.m_fd = cfd;
		ret.m_state = SocketState::Connected;
		return 0;
	}

	int socket::send(const char* data, size_t size, int flags) {
    	__label__ __err__;
    	int ret = ::send(m_fd, data, size, flags);	
    	if (ret < 0) {
    		setError("send", errno);	
		}
		return ret;	

		__err__:
		close();
		return -1;
    }

    int socket::recv(char* data, size_t size, int flags) {
    	int ret = ::recv(m_fd, data, size, flags);	
    	
    	if (ret < 0) {
    		setError("recv", errno);	
		}
		return ret;	
    }


	int socket::writeData(const char* str, size_t sz) {
                return socket::send(str, sz, 0);
	}	

	int socket::readData(char* str, size_t sz) {
                return socket::recv(str, sz, 0);
	}

}

/*
	socket(int32_t ip, int port, uint8_t family = AF_INET) {
		init(ip,port,family);
	}

	void init(int32_t ip, int port, uint8_t family = AF_INET) {
		addr.sin_family = family;
		addr.sin_port = htons(port);
   	 	addr.sin_addr.s_addr = htonl(ip);	
	}

	void init(const char* ip, int port, uint8_t family = AF_INET) {
		addr.sin_family = family;
		addr.sin_port = htons(port);
   	 	addr.sin_addr.s_addr = inet_addr(ip);	
	}

	int connect(int32_t ip, int port, uint8_t family = AF_INET) {
		init(ip, port, family);
		if (open()) return -1;
		return connect();
	}

	int connect(const char* ip, int port, uint8_t family = AF_INET) {
		init(ip, port, family);
		if (open()) return -1;
		return connect();
	}

	

	int disconnect() {
		int ret = ::shutdown(fd, SHUT_RDWR);
		if (ret < 0) {
   			m_errstr = strerror(errno);
   			return -1;
   		}

		ret = ::close(fd);
		if (ret < 0) {
   			m_errstr = strerror(errno);
   			return -1;
   		}
   		
   		return 0;
	}

	int bind() {
		if (::bind(fd, (struct sockaddr*) &addr, sizeof(addr)) < 0) {
   			m_errstr = strerror(errno);
   			return -1;				
		}
		return 0;			 
	}

	int connect() {
		if (::connect(fd, (struct sockaddr*) &addr, sizeof(addr)) < 0) {
   			m_errstr = strerror(errno);
   			return -1;				
		}
		
		return 0;			 
	}

    int listen(int con) {
		if (::listen(fd, con) < 0) {
   			m_errstr = strerror(errno);
   			return -1;				
		}
		return 0;		
    }

    

    int write(const char* data, size_t size) {
    	return send(data, size, 0);
    }

    int read(char* data, size_t size) {
    	return recv(data, size, 0);
    }

    bool blocking(bool en)
	{
	   if (fd < 0) return false;
	   int flags = fcntl(fd, F_GETFL, 0);
	   if (flags < 0) return false;
	   flags = en ? (flags&~O_NONBLOCK) : (flags|O_NONBLOCK);
	   return (fcntl(fd, F_SETFL, flags) == 0) ? true : false;
	}

	int reusing(bool en) {
		int on = en;
		int rc = setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (char *) &on, sizeof (on));
		return rc;
	}

	int nodelay(bool en) {
		int on = en;
		int rc = setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, (char *) &on, sizeof (on));
		return rc;
	}

	gxx::io::text_stream_reader as_text_reader() {
		return gxx::io::text_stream_reader(*this);
	}

	void setFileDescriptor(int newfd) {
		fd = newfd;
	}

	int32_t ip() { return addr.sin_addr.s_addr; }
	int32_t port() { return addr.sin_port; }
	int32_t family() { return addr.sin_family; }

	const gxx::string& errorString() { return m_errstr; }
	
	void clean_input() {
		char buf[128];
		while(int ret = recv(buf, 128, MSG_DONTWAIT) >= 0) {}
	}
*/
