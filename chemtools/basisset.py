#import pymongo
import copy
import decimal
import numpy as np
from itertools import chain
from collections import OrderedDict

_shells = ["s", "p", "d", "f", "g", "h", "i"]

class BasisSet:
    '''
    Basis set module supporting basic operation on basis sets and can be used
    as a API for mongoDB basis set repository.
    '''

    @classmethod
    def from_dict(cls, d):
        '''
        Initialize the BasisSet object from a general dictionary with an
        assumed structure of "functions" entry. This method can be used to
        initialize the BasisSet object directly from mongoDB database.
        '''
        if isinstance(d, dict):
            bs = cls()
            for key, val in d.items():
                if key == 'functions':
                    setattr(bs, key, OrderedDict(sorted(val.items(), key=lambda x: _shells.index(x[0]))))
                else:
                    setattr(bs, key, val)
        return bs

    @classmethod
    def from_optdict(cls, x0, bsoptdict):

        icount  = 0
        skipped = 0
        functions = dict()
        for lqn, nf in enumerate(bsoptdict["nfpshell"]):
            if nf == 0:
                skipped += 1
                continue
            functions[_shells[lqn]] = dict()
            if bsoptdict["typ"].lower() in ["direxp", "direct", "exps", "exponents"]:
                exps = list(x0[icount:icount+nf])
                icount += nf
                functions[_shells[lqn]]['exponents'] = exps
            elif bsoptdict["typ"].lower() in ["even", "eventemp", "eventempered"]:
                groups = group(x0, 2)
                exps = eventemp(nf, groups[lqn-skipped])
                functions[_shells[lqn]]['exponents'] = exps
            elif bsoptdict["typ"].lower() in ["well", "welltemp", "welltempered"]:
                groups = group(x0, 4)
                exps = welltemp(nf, groups[lqn-skipped])
                functions[_shells[lqn]]['exponents'] = exps
            elif bsoptdict["typ"].lower() in ["legendre"]:
                npar = len(bsoptdict["params"][lqn-skipped])
                pars = x0[icount:icount+npar]
                exps = legendre(nf, pars)
                functions[_shells[lqn]]['exponents'] = exps
                icount += npar
        bs = cls()
        setattr(bs, 'functions', cls.add_coeffs(functions))
        for key in bsoptdict.keys():
            if key != "functions":
                setattr(bs, key, bsoptdict[key])
        return bs

    @staticmethod
    def add_coeffs(functions):
        '''
        for every exponent in the "exponents" list add a 1 function with
        contraction coefficient equal to 1.0
        '''

        for shell, fs in functions.items():
            fs['contractedfs'] = list()
            for i, expt in enumerate(fs['exponents']):
                fs['contractedfs'].append({'indices' : [i], 'coefficients' : [1.0]})
        return functions

    def __repr__(self):
        res = "<BasisSet(\n"
        for key, val in self.__dict__.items():
            res += "\t{k:<20s} = {v}\n".format(k=key, v=val)
        res += ")>"
        return res

    def __str__(self):
        res = "<BasisSet(\n"
        for key, val in self.__dict__.items():
            res += "\t{k:<20s} = {v}\n".format(k=key, v=val)
        res += ")>"
        return res

    def __add__(self, bs2add):

        if not isinstance(bs2add, BasisSet):
            raise TypeError('only instances of "BasisSet" class can be added')

        for oshell, ofs in bs2add.functions.items():
            if oshell.lower() in self.functions.keys():
                if self.common_floats(self.functions[oshell]['exponents'], ofs['exponents']):
                    exps, indx = self.merge_list_of_floats(self.functions[oshell.lower()]['exponents'], ofs['exponents'])
                    self.functions[oshell.lower()]['exponents'] = exps
                    for cf in ofs['contractedfs']:
                        newc = copy.copy(cf)
                        newc['indices'] = [indx[i] for i in newc['indices']]
                        self.functions[oshell.lower()]['contractedfs'].append(newc)
                else:
                    nexp = len(self.functions[oshell.lower()]['exponents'])
                    self.functions[oshell.lower()]['exponents'].extend(ofs['exponents'])
                    for cf in ofs['contractedfs']:
                        newc = copy.copy(cf)
                        newc['indices'] = [i + nexp for i in newc['indices']]
                        self.functions[oshell.lower()]['contractedfs'].append(newc)
            else:
                self.functions[oshell] = ofs

    def add(self, bs2add):
        '''
        Merge functions to the BasisSet object "functions" attribute from
        another BasisSet object if the "element" atrribute has the same value.
        '''

        if bs2add is not None and self.element == bs2add.element:
            for oshell, ofs in bs2add.functions.items():
                if oshell.lower() in self.functions.keys():
                    if self.common_floats(self.functions[oshell]['exponents'], ofs['exponents']):
                        exps, indx = self.merge_list_of_floats(self.functions[oshell.lower()]['exponents'], ofs['exponents'])
                        self.functions[oshell.lower()]['exponents'] = exps
                        for cf in ofs['contractedfs']:
                            newc = copy.copy(cf)
                            newc['indices'] = [indx[i] for i in newc['indices']]
                            self.functions[oshell.lower()]['contractedfs'].append(newc)
                    else:
                        nexp = len(self.functions[oshell.lower()]['exponents'])
                        self.functions[oshell.lower()]['exponents'].extend(ofs['exponents'])
                        for cf in ofs['contractedfs']:
                            newc = copy.copy(cf)
                            newc['indices'] = [i + nexp for i in newc['indices']]
                            self.functions[oshell.lower()]['contractedfs'].append(newc)
                else:
                    self.functions[oshell] = ofs
        else:
            return

    def print_exponents(self):

        for shell, fs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            for exp in fs['exponents']:
                print("{s:10s}  {e:>25.10f}".format(s=shell, e=exp))

    @staticmethod
    def common_floats(lof, reflof):

        c = decimal.Context(prec=6)
        decimal.setcontext(c)
        D = decimal.Decimal

        l    = [D(x)*1 for x in lof]
        refl = [D(x)*1 for x in reflof]
        return any(D('0') == x.compare(y) for x in l for y in refl)

    @staticmethod
    def merge_list_of_floats(lof, lof2add, prec=6):
        '''
        merge a list of floats "lof2add" into a reference list
        of floats "lof" ommitting duplicate floats and return
        merged list and indices of newly added floats in the reference list.

        Args:
            lof (list of floats)
                reference list of floats to which new floats will be appended
            lof2add (list of floats)
                list of floats to be added to the reference list
            prec (int)
                precision (number of significant digits used in float comparison
                default=6
        Returns:
            lof (list of floats)
                appended list of floats
            newidx (list of integers)
                list of integers corresponding to the indices of newly added floats
        '''

        c = decimal.Context(prec=prec)
        decimal.setcontext(c)
        D = decimal.Decimal

        expref  = [D(x)*1 for x in lof]
        exp2add = [D(x)*1 for x in lof2add]
        nexp = len(lof)
        newidx = list()
        for addexp in exp2add:
            if addexp in expref:
                newidx.append(expref.index(addexp))
            else:
                expref.append(addexp)
                newidx.append(expref.index(addexp))
        for addidx, addexp in zip(newidx, lof2add):
            if addidx > nexp:
                lof.append(addexp)
        return lof, newidx


    def write_dalton(self, efmt="20.10f", cfmt="15.8f"):
        '''
        Return a string with the basis set in DALTON format.

        Args:
            efmt (str)
                string describing output format for the exponents, default:
                "20.10f"
            cfmt (str)
                string describing output format for the contraction
                coefficients, default: "15.8f"

        Returns:
            res (str)
                basis set string
        '''

        res = "! {s}\n".format(s=self.name)
        for shell, shellfs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            res += "! {s} functions\n".format(s=shell)
            res += "{f:1s}{p:>4d}{c:>4d}\n".format(f="F", p=len(shellfs["exponents"]), c=len(shellfs["contractedfs"]))
            for i, expt in enumerate(shellfs["exponents"]):
                cc = [cfs["coefficients"][cfs["indices"].index(i)] if i in cfs["indices"] else 0.0 for cfs in shellfs["contractedfs"]]
                res += "{e:>{efmt}}{c}".format(e=expt, efmt=efmt, c="".join(["{0:{cfmt}}".format(c, cfmt=cfmt) for c in cc])) + "\n"
        return res

    def write_gamess(self, efmt="20.10f", cfmt="15.8f"):
        '''
        Return a string with the basis set in GAMESS(US) format.

        Args:
            efmt (str)
                string describing output format for the exponents, default:
                "20.10f"
            cfmt (str)
                string describing output format for the contraction
                coefficients, default: "15.8f"

        Returns:
            res (str)
                basis set string
        '''

        res = ""
        for shell, shellfs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            for contraction in shellfs["contractedfs"]:
                res += "{s:<1s}{n:>3d}\n".format(s=shell.upper(), n=len(contraction["indices"]))
                for i, (idx, coeff) in enumerate(zip(contraction["indices"], contraction["coefficients"]), start=1):
                    res += "{i:3d}{e:>{efmt}}{c:>{cfmt}}".format(i=i, e=shellfs["exponents"][idx], efmt=efmt, c=coeff, cfmt=cfmt)+ "\n"
        return res + "\n"

    def write_molpro(self, efmt="20.10f", cfmt="15.8f"):
        '''
        Return a string with the basis set in MOLPRO format.

        Args:
            efmt (str)
                string describing output format for the exponents, default:
                "20.10f"
            cfmt (str)
                string describing output format for the contraction
                coefficients, default: "15.8f"

        Returns:
            res (str)
                basis set string
        '''

        res = ""
        for shell, shellfs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            exps = ", ".join(["{0:>{efmt}}".format(e, efmt=efmt).lstrip() for e in shellfs["exponents"]])
            res += "{s:>s}, {e:>s}, ".format(s=shell, e=self.element) + exps + '\n'
            for contraction in shellfs["contractedfs"]:
                coeffs = ", ".join(["{0:>{cfmt}}".format(c, cfmt=cfmt).lstrip() for c in contraction["coefficients"]])
                res += "c, {0:d}.{1:d}, ".format(min(contraction["indices"])+1, max(contraction["indices"])+1) + coeffs + '\n'
        return res


    def write_nwchem(self, efmt="20.10f", cfmt="15.8f"):
        '''
        Return a string with the basis set in NWChem format.

        Args:
            efmt (str)
                string describing output format for the exponents, default:
                "20.10f"
            cfmt (str)
                string describing output format for the contraction
                coefficients, default: "15.8f"

        Returns:
            res (str)
                basis set string
        '''

        res = 'BASIS "ao basis" PRINT\n'
        for shell, shellfs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            res += "{e} {s}\n".format(e=self.element, s=shell)
            for i, expt in enumerate(shellfs["exponents"]):
                cc = [cfs["coefficients"][cfs["indices"].index(i)] if i in cfs["indices"] else 0.0 for cfs in shellfs["contractedfs"]]
                res += "{e:>{efmt}}{c}".format(e=expt, efmt=efmt, c="".join(["{0:{cfmt}}".format(c, cfmt=cfmt) for c in cc])) + '\n'
        return res + "END\n"

    def contraction_scheme(self):
        '''
        Return a string describing the contraction scheme.
        '''

        cs, ec = [], []
        for shell, shellfs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            cs.append((shell, len(shellfs["exponents"]), len(shellfs["contractedfs"])))
            ec.append([len(cfs["indices"]) for cfs in shellfs["contractedfs"]])
        return "({p:s}) -> [{c:s}] : {{{ec}}}".format(
                p="".join(["{0:d}{1:s}".format(c[1], c[0]) for c in cs]),
                c="".join(["{0:d}{1:s}".format(c[2], c[0]) for c in cs]),
                ec="/".join(["".join(["{0:d}".format(c) for c in x]) for x in ec]))

    @staticmethod
    def get_spherical(l):
        '''
        Calculate the number of spherical components of a function with a given angular
        momentum value "l".
        '''
        return 2*l+1

    @staticmethod
    def get_cartesian(l):
        '''
        Calculate the number of cartesian components of a function with a given angular
        momentum value "l".
        '''
        return int((l+1)*(l+2)/2)

    def nf(self, spherical=True):
        '''
        Calculate the number of basis functions

        Args:
            spherical (Bool)
                flag indicating if spherical or cartesian functions should be
                used, default: True

        Returns:
            res (int)
                number of basis functions
        '''

        if spherical:
            return sum(self.get_spherical(_shells.index(shell))*len(shellfs["contractedfs"]) for shell, shellfs in self.functions.items())
        else:
            return sum(self.get_cartesian(_shells.index(shell))*len(shellfs["contractedfs"]) for shell, shellfs in self.functions.items())

    def uncontract(self):
        '''
        Uncontract the basis set. This replaces the contraction coefficients in
        the current object.
        '''

        for shell, shellfs in sorted(self.functions.items(), key=lambda x: _shells.index(x[0])):
            shellfs["contractedfs"] = [{"indices" : [i], "coefficients" : [1.0]} for i, e in enumerate(shellfs["exponents"])]

    @classmethod
    def uncontracted(cls, bs):
        '''
        Return a new BasisSet object with uncotracted version of the basis.
        '''
        bsnew = copy.deepcopy(bs)
        for shell, shellfs in sorted(bsnew.functions.items(), key=lambda x: _shells.index(x[0])):
            shellfs["contractedfs"] = [{"indices" : [i], "coefficients" : [1.0]} for i, e in enumerate(shellfs["exponents"])]
        return bsnew

    def primitives_per_shell(self):
        return [len(f["exponents"]) for s, f in sorted(self.functions.items(), key=lambda x: _shells.index(x[0]))]

    def contractions_per_shell(self):
        return [len(f["contractedfs"]) for s, f in sorted(self.functions.items(), key=lambda x: _shells.index(x[0]))]

    def primitives_per_contraction(self):
        return [[len(c["indices"]) for c in f["contractedfs"]] for s, f in sorted(self.functions.items(), key=lambda x: _shells.index(x[0]))]

    def contraction_type(self):
        '''
        Determine the contraction type: segmented, general, uncontracted, unknown
        '''

        pps = self.primitives_per_shell()
        cps = self.contractions_per_shell()
        ppc = self.primitives_per_contraction()

        if any(x > 1 for x in pps):
            if all(all(x == 1 for x in shell) for shell in ppc):
                return "uncontracted"
            elif all(all(pinc == np for pinc in shell) for np, shell in zip(pps, ppc)):
                return "general"
            else:
                return "unknown"

        # one function per shell case
        if all(all(x == 1 for x in shell) for shell in ppc):
            return "uncontracted 1fps"

def zetas2legendre(zetas, kmax):
    '''
    From a set of exponents "zetas", using least square fit calculate the
    expansion coefficients into the legendre polynomials of the order "kmax".

    Args:
        kmax (int)
            length of the legendre expansion
        zetas (list)
            list of exponents (floats) to be fitted

    Returns:
        coeff (np.array)
            numpy array of legendre expansion coeffcients of length kmax
    '''

    # exponents should be sorted in the acsending order
    zetas = sorted(zetas)
    c = np.asarray([1.0]*kmax, dtype=float)

    leg = np.polynomial.Legendre(c)
    a = np.zeros((len(zetas), kmax))

    for j in range(len(zetas)):
        for k in range(kmax):
            arg = (2.0*(j+1.0)-2.0)/(len(zetas)-1.0)-1.0
            a[j, k] = leg.basis(k)(arg)

    return np.linalg.lstsq(a, np.log(zetas))[0]

def eventemp(nf, params):
    '''
    Generate a sequence of nf even tempered exponents accodring to
    the even tempered formula zeta_i = alpha * beta**(i-1),

    Args:
        nf (int)
            number fo exponents to generate
        params (tuple)
            alpha and beta parameters
    Returns:
        res (list)
            list of generated exponents (floats)
    '''
    if not isinstance(nf, int):
        raise TypeError('"nf" variable should be of "int" type, got: {}'.format(type(nf)))
    if len(params) !=  2:
        raise ValueError('"params" tuple should have exactly 2 entries, got {}'.format(len(params)))

    alpha, beta = params
    return [alpha * np.power(beta, i) for i in range(nf)]

def welltemp(nf, params):
    '''
    Generate a sequence of nf well tempered exponents accodring to
    the well tempered fromula
    zeta_i = alpha * beta**(i-1) * [1 + gamma * (i/nf)**delta]

    Args:
        nf (int)
            number fo exponents to generate
        params (tuple)
            alpha, beta, gamma and delta parameters
    Returns:
        res (list)
            list of generated exponents (floats)
    '''
    if not isinstance(nf, int):
        raise TypeError('"nf" variable should be of "int" type, got: {}'.format(type(nf)))
    if len(params) !=  4:
        raise ValueError('"params" tuple should have exactly 4 entries, got {}'.format(len(params)))

    alpha, beta, gamma, delta = params
    return [alpha*np.power(beta, i)*(1+gamma*np.power((i+1)/nf, delta)) for i in range(nf)]

def legendre(nf, coeffs):
    '''
    Generate a sequence of nf exponents from expansion in the orthonormal
    legendre polynomials as described in:
    Peterson, G. A. et.al J. Chem. Phys., Vol. 118, No. 3 (2003).
    '''
    if not isinstance(nf, int):
        raise TypeError('"nf" variable should be of "int" type, got: {}'.format(type(nf)))
    if len(coeffs) <  1:
        raise ValueError('"coeffs" tuple should have at least 1 entry, got {}'.format(len(coeffs)))

    # special case for one function
    if len(coeffs) == 1:
        return [np.exp(coeffs[0])] 

    poly = np.polynomial.legendre.Legendre(coeffs)
    zetas = [poly(((2.0*(i+1.0)-2.0)/(nf-1.0))-1.0) for i in range(nf)]
    return [np.exp(x) for x in zetas]

def group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]

    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.

    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    return list(zip(*[lst[i::n] for i in range(n)]))

def get_x0(basisopt):
    '''
    Collect all the parameters in a consecutive list of elements.
    '''

    return list(chain.from_iterable(basisopt["params"]))

def opt_shell_by_nf(shell=None, nfs=None, max_params=5, opt_tol=1.0e-4, save=False, bsopt=None, **kwargs):
    '''
    For a given shell optimize the functions until the convergence criterion is reached
    the energy difference for two consecutive function numbers is less than the threshold

    Kwargs:
        shell : (string)
            string label for the shell to be optimized

        nfs : (list of ints)
            list of integers representing the number of basis functions to be
            inceremented in the optimization,

        max_params : (int)
            maximal number of parameters to be used in the legendre expansion,
            (length of the expansion)

        opt_tol : (float)
            threshold controlling the termination of the shell optimization,
            if energy difference between two basis sets with subsequent number
            of functionsis larger than this threshold, another function is
            added to this shell and parameters are reoptimized,

        save : (bool)
            a flag to trigger saving all the optimized basis functions for each
            shell,

        **kwargs:
            options for the basis set optimization driver, see driver function
            from the basisopt module

    Returns:
        BasisSet object instance with optimized functions for the specified shell

    Raises:
        ValueError:
            when `shell` is different from `s`, `p`, `d`, `f`, `g`, `h`, `i`
            when number of parameters equals 1 and there are more functions
            when there are more parameters than functions to optimize
    '''

    _shells = ['s', 'p', 'd', 'f', 'g', 'h', 'i']

    if shell not in _shells:
        raise ValueError('shell must be one of the following: {}'.format(", ".join(_shells)))

    if len(bsopt['params'][0]) == 1 and min(nfs) != 1:
        raise ValueError("1 parameter and {0} functions doesn't make sense".format(min(nfs)))

    if min(nfs) < len(bsopt['params'][0]):
        raise ValueError("more parameters ({0}) than functions to optimize ({1})".format(len(bsopt['params'][0]), min(nfs)))

    bsopt["typ"] = "legendre"
    e_last = 0.0
    x_last = bsopt['params'][0]

    for nf in nfs:
        bsopt['nfpshell'] = [0]*_shells.index(shell) + [nf]
        res = driver(bsopt=bsopt, **kwargs)

        print "Completed optimization for {0:d} {1}-type functions".format(nf, shell)

        print "{s:<25s} : {v:>20.10f}".format(s="Current Function value", v=res.fun)
        print "{s:<25s} : {v:>20.10f}".format(s="Previous Function value", v=e_last)
        print "{s:<25s} : {v:>20.10f}".format(s="Difference", v=abs(res.fun-e_last))

        if abs(res.fun - e_last) < opt_tol:
            print("Basis saturated with respect to threshold")
            bsopt['nfpshell'] = nfps_last
            if save:
                save_basis(x_last, bsopt)
            return BasisSet.from_optdict(x_last, bsopt)
        else:
            print("Threshold exceeded, continuing optimization.")
            x_last = res.x.tolist()
            nfps_last = bsopt['nfpshell']
            if len(bsopt['params'][0]) < max_params:
                print "adding more parameters"
                restup = tuple(res.x)
                # this assumption should be revised, improved or justified
                # suggestion: maybe change to average of existing parameters
                restup += tuple([abs(min(restup)*0.25)])
                bsopt['params'] = [restup,]
            else:
                print "not adding more parameters"
                bsopt['params'] = [tuple(res.x),]
            e_last = res.fun
    else:
        print "Supplied number of functions exhausted but the required accuracy was not reached"
        if save:
            save_basis(res.x.tolist(), bsopt)
        return BasisSet.from_optdict(res.x.tolist(), bsopt)

def opt_multishell(shells=None, nfps=None, guesses=None, max_params=5, opt_tol=1.0e-4, save=False, bsopt=None, **kwargs):
    '''
    Optimize a basis set by saturating the function space shell by shell

    Kwargs:
        shells (list of strings):
            list of shells to be optimized, in the order the optimization should
            be performed,

        nfps (list of lists of integers):
            list specifying a set of function numbers to be scanned per each
            shell,

        guesses (list of lists of floats):
            list specifying a set of starting parameters per each shell,

        max_params (int)
            maximal number of parameters to be used in the legendre expansion,
            (length of the expansion)

        opt_tol (float):
            threshold controlling the termination of the shell optimization,
            if energy difference between two basis sets with subsequent number
            of functionsis larger than this threshold, another function is
            added to this shell and parameters are reoptimized

        **kwargs:
            options for the basis set optimization driver, see driver function
            from the basisopt module
    '''

    # bsnoopt needs to exists since it will be appended with optimized
    # functions after each shell is optimized
    if kwargs['bsnoopt'] is None:
        kwargs['bsnoopt'] = BasisSet.from_dict({"element"   : "Be",
                                      "functions" : {}})

    # begin the main loop over shells, nr f per shell and guesses
    for shell, nfs, guess in zip(shells, nfps, guesses):

        header = " Beginning optimization for {s:s} shell ".format(s=shell)
        print "="*100
        print format(header, '-^100')
        print "="*100

        bsopt['params'] = [tuple(guess)]
        # begin the optimization for a given shell and store the optimized
        # functions under optimized_shell
        optimized_shell = opt_shell_by_nf(shell, nfs, max_params=max_params,
                                          opt_tol=opt_tol, save=save,
                                          bsopt=bsopt, **kwargs)
        # add the optimized shell to the total basis set
        kwargs['bsnoopt'].add(optimized_shell)

    # save the final complete basis set
    basis_dict = vars(kwargs['bsnoopt'])
    with open("final.bas", 'wb') as ff:
        ff.write(str(basis_dict))

def main():
    pass

if __name__ == "__main__":
    main()
