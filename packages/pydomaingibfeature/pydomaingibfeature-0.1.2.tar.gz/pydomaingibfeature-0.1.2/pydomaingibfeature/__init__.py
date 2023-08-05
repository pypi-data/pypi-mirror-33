import os
import sys
import pygibberish as pygib



class PyDomainGibFeature: 
    """
    gibfeature
    """
    def __init__(self, dic): 
        root_path = os.path.dirname(os.path.realpath(__file__))
        ms = dic.get('mfiles', [
            os.path.join(root_path, "ch2.pki"),
            os.path.join(root_path, "ch3.pki"),
            os.path.join(root_path, "ch4.pki"),
            os.path.join(root_path, "en2.pki"),
            os.path.join(root_path, "en3.pki"),
            os.path.join(root_path, "en4.pki"),
            ])
        self.npart = dic.get('npart', 2)
        self.models = [pygib.Gibberish(m) for m in ms]

    def norm_dict(self): 
        norm = {}
        for i in xrange(self.range()):
            norm[i] = (0.0, 1.0)
        return norm

    def neednorm(self):
        """
        neednorm
        """
        return True
    
    def range(self): 
        return len(self.models) * self.npart

    def feature(self, dm):
        try: 
            fea = []
            cnt = 0
            for i in dm.split('.')[0:self.npart]:
                for gib in self.models: 
                   fea.append((cnt, float(gib.calc(i))))
                   cnt += 1
            return fea
        except Exception as e:
            sys.stderr.write('Get feature error for %s' % (str(e)))
            return []
