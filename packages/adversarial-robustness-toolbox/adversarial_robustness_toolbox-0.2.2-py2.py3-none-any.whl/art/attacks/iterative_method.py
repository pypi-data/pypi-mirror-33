from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np

from art.attacks import FastGradientMethod


class BasicIterativeMethod(FastGradientMethod):
    """
    The Basic Iterative Method is the iterative version of FGM and FGSM. If target labels are not specified, the
    attack aims for the least likely class (the prediction with the lowest score) for each input.
    Paper link: https://arxiv.org/abs/1607.02533
    """
    attack_params = ['norm', 'eps', 'eps_step']

    def __init__(self, classifier, norm=np.inf, eps=.3, eps_step=0.1):
        """
        Create a :class:`BasicIterativeMethod` instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param eps: Maximum perturbation that the attacker can introduce.
        :type eps: `float`
        :param eps_step: Attack step size (input variation) at each iteration.
        :type eps_step: `float`
        """
        # print('init bim')
        # super(BasicIterativeMethod, self).__init__(classifier, norm=norm, eps=eps, targeted=True)
        self.set_params(eps_step=eps_step)
        # print('exit init bim')

    def generate(self, x, **kwargs):
        """
        Generate adversarial samples and return them in an array.

        :param x: An array with the original inputs.
        :type x: `np.ndarray`
        :param eps: Maximum perturbation that the attacker can introduce.
        :type eps: `float`
        :param eps_step: Attack step size (input variation) at each iteration.
        :type eps_step: `float`
        :return:
        """
        self.set_params(**kwargs)
        adv_x = x.copy()

        # Choose least likely class as target prediction for the attack
        targets = np.argmin(self.classifier.predict(x), axis=1)
        active_indices = range(len(adv_x))

        # Set max iterations with heuristic from original paper
        nb_iter, max_iter = 0, int(min(self.eps + 4. * self.eps_step, 1.25 * self.eps))

        while len(active_indices) != 0 and nb_iter < max_iter:
            # Adversarial crafting
            adv_x[active_indices] = self._compute(adv_x[active_indices], targets[active_indices], self.eps_step)
            adv_x = np.clip(adv_x, x - self.eps, x + self.eps)
            adv_preds = self.classifier.predict(adv_x)

            # Update active indices
            active_indices = np.where(targets[active_indices] != np.argmax(adv_preds, axis=1))[0]
            nb_iter += 1

        return adv_x

    def set_params(self, **kwargs):
        """
        Take in a dictionary of parameters and applies attack-specific checks before saving them as attributes.

        :param eps: Maximum perturbation that the attacker can introduce.
        :type eps: `float`
        :param eps_step: Attack step size (input variation) at each iteration.
        :type eps_step: `float`
        """
        # print('set params bim')
        # print(kwargs.items())
        # Save attack-specific parameters
        # super(super(BasicIterativeMethod, self), self).set_params(**kwargs)
        # print('done setting')

        for key, value in kwargs.items():
            if key in self.attack_params:
                print('now setting', key)
                setattr(self, key, value)

        if self.eps_step > self.eps:
            raise ValueError('The iteration step `eps_step` has to be smaller than the total attack `eps`.')

        # print('exit set params bim')
        return True
