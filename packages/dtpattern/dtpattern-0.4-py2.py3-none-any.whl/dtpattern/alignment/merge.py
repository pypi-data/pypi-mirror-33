


from multipledispatch import dispatch

from dtpattern.alignment import utils


@dispatch(str,str)
def merge(alpha, beta):
    """

    :param alpha: ccharacter 1
    :param beta:
    :return: a list with the unique cset symbols
    """

    return list(set([utils.translate(alpha), utils.translate(beta)]))

@dispatch(list,list)
def merge(alpha, beta):
    return list(set(alpha+beta))

@dispatch(list,str)
def merge(alpha, beta):
    """

    :param alpha: cset symbols
    :param beta: original character
    :return: a list with the unique cset symbols
    """
    t = [utils.translate(beta)]
    return list(set(alpha + t))

@dispatch(str,list)
def merge(alpha, beta):
    # same as list, str, just flip the variables
    return merge(beta, alpha)

@dispatch(tuple, str)
def merge(alpha, beta):
    """

    :param alpha: tuple is an optional pattern
    :param beta:
    :return:
    """


    a10 = alpha[0]

    m= merge(a10, beta)

    m = (m, alpha[1], alpha[2])
    return m

@dispatch(tuple, tuple)
def merge(alpha, beta):

    m = merge(alpha[0], beta[0])

    m = (m, min(alpha[1],beta[1]), max(alpha[2],beta[2]))
    return m

@dispatch(list, tuple)
def merge(alpha, beta):
    b = beta[0]

    m = merge(alpha, b)

    m = (m, beta[1], beta[2])
    return m

@dispatch(tuple,list)
def merge(alpha, beta):
    return merge(beta, alpha)


@dispatch(str, tuple)
def merge(alpha, beta):
    """

    :param alpha:
    :param beta: tuple is an optional pattern
    :return:
    """
    return merge(beta,alpha)

    b = beta[0]

    m= merge(alpha, b)

    m = (m, beta[1], beta[2])
    return m
