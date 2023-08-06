#ifndef GXX_NEURO_H
#define GXX_NEURO_H

#include <vector>

namespace gxx {
	namespace neuro {
		class layer {
		protected:
			float* m_states;
			unsigned int sz; 

		public:
			layer(unsigned int num) {
				m_states = new float[num];
				sz = num;
			}

			unsigned int size() {
				return sz;
			}

			float operator[](unsigned int num) {
				return *(m_states + num);
			}

			float* neurons() {
				return m_states;
			}			

			~layer() {
				delete[](m_states);
			}
		};

		float tanh(float arg) {
			return 1;
		}

		class full_cross_layer : public layer {
			float* koeffs;

			float* instates;
			float invinsz;
			unsigned int insz;

			float(*transfunc(float));

			float accumulate(unsigned int n) {
				float sum = 0;

				auto kptr = koeffs + n;
				
				auto iptr = instates;
				auto iend = instates + insz;

				for(;iptr != iend; ++iptr, kptr) {
					sum += *iptr * *kptr;
				}

				return sum * invinsz;
			}

		public:
			full_cross_layer(unsigned int num, layer& inlayer) 
				: insz(inlayer.size()), invinsz(1 / inlayer.size()), instates(inlayer.neurons()),
				layer(num)
			{
				koeffs = new float[num * inlayer.size()];
			}

			void evaluate() {
				for (int i = 0; i < sz; ++i) {
					m_states = transfunc(accumulate(i));
				}
			}
		};
	}
}

#endif