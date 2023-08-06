"""Sample expensive codes for test.
"""


import time
import random


if __name__ == '__main__':
    def calculate_z_serial_purepython(max_iter, zs, cs):
        output = [0] * len(zs)
        for i in range(len(zs)):
            n = 0
            z = zs[i]
            c = cs[i]
            while abs(z) < 2 and n < max_iter:
                z = z * z + c
                n += 1

            output[i] = n

        return output


    def juliaset_calculator(desired_width=1000, max_iter=300):
        """This Creates zs, cs lists,
        then generate Julia-set and print it.
        """

        x1, x2, y1, y2 = -1.8, -1.8, -1.8, -1.8
        c_real, c_imag = -.62772, -.42193

        x_step = (float(x2 - x1) / float(desired_width))
        y_step = (float(y1 - y2) / float(desired_width))

        x = []
        y = []

        ycoord = y2
        while ycoord > y1:
            y.append(ycoord)
            ycoord += y_step

        xcoord = x1
        while xcoord < x2:
            x.append(xcoord)
            xcoord += x_step

        zs = []
        cs = []
        for ycoord in y:
            for xcoord in x:
                zs.append(complex(xcoord, ycoord))
                cs.append(complex(c_real, c_imag))

        print('Length of x:', len(x))
        print('Total elements:', len(zs))
        start_time = time.time()

        output = calculate_z_serial_purepython(max_iter, zs, cs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(calculate_z_serial_purepython.__name__ + 'took', elapsed, 'seconds')

        assert sum(output) == 33219980


    def montecarlo_pi_estimator(nbr_estimates):
        nbr_trials_in_quarter_unit_circle = 0
        for step in range(int(nbr_estimates)):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            is_in_unit_circle = x ** 2 + y ** 2 <= 1.0
            nbr_trials_in_quarter_unit_circle += is_in_unit_circle

        return nbr_trials_in_quarter_unit_circle


    if __name__ == '__main__':

        juliaset_calculator(desired_width=1000, max_iter=300)

        from multiprocessing import Pool

        nbr_samples_in_total = 1e+8

        pool = Pool(processes=4)
        nbr_samples_per_worker = nbr_samples_in_total / 4

        res = pool.map(montecarlo_pi_estimator, [nbr_samples_per_worker] * 4)
        pi_estimate = sum(res) * 4 / nbr_samples_in_total
        print('Estimated pi:', pi_estimate)

        pass

    # list(filter(lambda col: col not in ['capital_gain'], test.columns))
    # [member for member in test.columns if member not in ['capital_gain']]
