#ifndef GXX_SHARED_PTR_H
#define GXX_SHARED_PTR_H

#include <gxx/utility.h>
#include <inttypes.h> 
#include <gxx/allocator.h>

namespace gxx {

	template<typename T>
	class default_deleter {
	public:
		void operator()(T* ptr) { 
			delete ptr; 
		}
	};

	template<typename T>
	class empty_deleter {
	public:
		void operator()(T* ptr) {}
	};

	class shared_control_block {
	public:
		uint16_t refs;

		void addref() { refs++; }
		void remref() { 
			refs--; 
			if (refs == 0) destroy();
		}

		virtual void destroy() = 0;
	};

	template <typename T, typename Deleter = default_deleter<T>>
	class shared_control_block_del : public shared_control_block, public Deleter {
		T* ptr;
		void destroy() { 
			Deleter::operator()(ptr); 
			delete this; 
		}

	public:
		shared_control_block_del() {}
		shared_control_block_del(T* ptr) : ptr(ptr) {}
	};

	//Объявление для friend механики.
	template <typename T> class shared_ptr;
	template <class T, class... Args> shared_ptr<T> make_shared(Args&& ...args);

	template <typename T>
	class shared_ptr {	
	private:
		T* ptr;
		shared_control_block* ctrl;

	public:
		shared_ptr() : ptr(nullptr), ctrl(nullptr) {}

		explicit shared_ptr(T* p) : ptr(p), ctrl(new shared_control_block_del<T>(p)) {
			ctrl->addref();
		}

		shared_ptr(const shared_ptr& other) : ptr(other.ptr), ctrl(other.ctrl) {
			if (ptr) ctrl->addref();
		}

		shared_ptr(nullptr_t ptr) : shared_ptr() {}

		~shared_ptr() {
			if (ptr) ctrl->remref();
		}

		shared_control_block* get_control_block() {
			return ctrl;
		}

		
		/*shared_ptr(pointer p, delete_fn d) : ptr(p), cnt( new counter(1) ), del(d) {
				gxx::cout << "shared_ptr(pointer, delete_fn)\n";
		}
	
		shared_ptr(const shared_ptr &x) : shared_ptr(x.ptr, x.del) {
				cnt = x.cnt;
				++*cnt;
				gxx::cout << "shared_ptr(const shared_ptr&)\n";
		}
	
		shared_ptr(shared_ptr &&x)
				: ptr( gxx::move(x.ptr) ),
				  cnt( gxx::move(x.cnt) ),
				  del( gxx::move(x.del) )
		{
				gxx::cout << "shared_ptr(shared_ptr&&)\n";
				x.ptr = nullptr;
				x.cnt = nullptr;
		}
	
		shared_ptr& operator = (const shared_ptr &x)
		{
				gxx::cout << "shared_ptr::operator=&\n";
				if (this != &x) {
						reset();
						ptr = x.ptr;
						cnt = x.cnt;
						del = x.del;
						++*cnt;
				}
				return *this;
		}
	
		shared_ptr& operator = (shared_ptr &&x)
		{
				gxx::cout << "shared_ptr::operator=&&\n";
				shared_ptr::swap(x);
				return *this;
		}
	
		void swap(shared_ptr &x)
		{
				gxx::cout << "shared_ptr::swap(shared_ptr&)\n";
				gxx::swap(ptr, x.ptr);
				gxx::swap(cnt, x.cnt);
				gxx::swap(del, x.del);
		}
	
	*/
		T* operator -> () const noexcept
		{
			return ptr;
		}
	
		T& operator * () const noexcept
		{
			return *ptr;
		}
	
		T* get() const noexcept
		{
			return ptr;
		}
	
		explicit operator bool() const noexcept
		{
			return ptr != nullptr;
		}
	
		bool unique() const noexcept {
			return use_count() == 1;
		}
	
		uint16_t use_count() const noexcept {
			return ctrl != nullptr ? ctrl->refs : 0;
		}
	
		void reset()
		{
				this->~shared_ptr();
				ptr = nullptr;
				ctrl = nullptr;
		}
	
		void reset(T* p)
		{
				reset();
				new (this) shared_ptr(p);
		}
	
		/*
		void reset(pointer p, delete_fn d)
		{
				reset();
				cnt = new counter(1);
				ptr = p;
				del = d;
		}*/

		template <typename T1, class... Args>
		friend shared_ptr<T1> make_shared(Args&& ...args);
	};

	template <typename T, class... Args>
	shared_ptr<T> make_shared(Args&& ...args) {
		shared_ptr<T> sptr;

		using Pair = gxx::pair<shared_control_block_del<T, empty_deleter<T>>, T>;
		gxx::allocator<Pair> m_alloc;
		auto pair = m_alloc.allocate(1);
		
		new (&pair->second) T(std::forward<Args>(args) ...);
		new (&pair->first) shared_control_block_del<T, empty_deleter<T>>(&pair->second);
		sptr.ptr = &pair->second;
		sptr.ctrl = &pair->first;

		return sptr;
	}	

	/*class shared_object {
	protected:
		uint16_t refs;

		void addref() { refs++; }
		void remref() { 
			refs--; 
			if (refs == 0) destroy();
		}

		shared_object() : refs(0) {}

	private:
		void destroy() {
			delete this;
		}
	};*/
}

#endif