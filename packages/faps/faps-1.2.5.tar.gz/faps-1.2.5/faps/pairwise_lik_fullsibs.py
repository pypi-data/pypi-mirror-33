import numpy as np
from alogsumexp import alogsumexp

def pairwise_lik_fullsibs(paternity_probs, exp = False):
    """
    Create a matrix of probabilities that each pair of individuals in a
    half-sibling array are full siblings.

    If two individuals are full siblings, the likelihood is the product of the
    likelihoods that each is fathered by father i, or father j, etc. We therefore
    take the product of likelihoods for paternity for each candidtae, and sum
    across the products for each father to account for uncertainty.

    The majority of fathers will not contribute to paternity, but will cause
    noise in the estimation of pairwise sibship probability. For this reason the
    function works much better if the likelihood array has had most unlikely
    fathers, for example by setting the likelihood for fathers with three or
    more opposing homozygous loci to zero.

    Parameters
    ----------
    paternity_probs: array
        array of posterior probabilities of paternity.
    exp: bool, optional
        If True, probabilities of paternity are exponentiated before calculating
        pairwise probabilities of sibships. This gives a speed boost if this is
        to be repeated many times, but there may be a cost to accuracy (this is 
        untested!).

    Returns
    -------
    A noffspring*noffspring matrix of log likelihoods of
    being full siblings.

    Example
    -------
    import numpy as np
    from faps import *

    # generate 4 families of 5 offspring
    allele_freqs = np.random.uniform(0.3, 0.5, 50)
    males = make_parents(200, allele_freqs)
    offspring = make_sibships(males, 0, range(1,5), 5)

    # Add muations
    mu = 0.0013
    males = males.dropouts(0.01).mutations(mu)
    offspring= offspring.dropouts(0.01).mutations(mu)

    mothers = males.subset(offspring.parent_index('m', males.names))
    patlik = paternity_array(offspring, mothers, males, allele_freqs, mu)

    prob_paternities = patlik.prob_array
    # Matrix of pairwise probabilities of being full siblings.
    fullpairs = pairwise_lik_fullsibs(prob_paternities)
    """
    lik_array = np.copy(paternity_probs)
    # pull out the number of offspring and parents
    noffs     = lik_array.shape[0]
    nparents  = lik_array.shape[1]

    #lik_array = lik_array - alogsumexp(lik_array, 1).reshape([noffs, 1]) # normalise to unity.
    if exp is False:
        # this section of code calculates the matrix in log space, but I found it quicker to exponentiate (below).
        # take all pairwise products of sharing fathers.
        pairwise_lik = np.array([alogsumexp(lik_array[x] + lik_array[y], axis=0) for x in range(noffs) for y in range(noffs)])
        pairwise_lik = pairwise_lik.reshape([noffs, noffs])

        return pairwise_lik
    if exp is True:
        # the sum can be quicker if you exponentiate, but this may harm precision.
        exp_array = np.exp(lik_array)
        # for each pair of offspring, the likelihood of not sharing each father.
        pairwise_lik = np.matmul(exp_array, exp_array.T)
        pairwise_lik = np.array(pairwise_lik).reshape([noffs, noffs]) # reshape

        return np.log(pairwise_lik)
