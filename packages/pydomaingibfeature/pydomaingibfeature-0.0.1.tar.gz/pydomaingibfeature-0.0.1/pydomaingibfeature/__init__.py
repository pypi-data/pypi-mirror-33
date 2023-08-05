import os
import pygibberish as pygib



class PyDomainGibFeature: 
    """
    gibfeature
    """
    def __init__(self, dic): 
        root_path = os.path.dirname(os.path.realpath(__file__))
        ms = dic.get('mfiles', [
            os.path.join(root_path, "ch3.pki"),
            os.path.join(root_path, "ch4.pki"),
            os.path.join(root_path, "ch5.pki"),
            os.path.join(root_path, "en3.pki"),
            os.path.join(root_path, "en4.pki"),
            os.path.join(root_path, "en5.pki"),
            ])
        self.npart = dic.get('npart', 2)
        self.models = [pygib.Gibberish(m) for m in ms]

    def neednorm(self):
        """
        neednorm
        """
        return True
    
    def range(self): 
        return len(self.models) * self.npart

    def feature(self, dm):
        fea = []
        cnt = 0
        for i in dm.split('.')[0:self.npart]:
            for gib in self.models: 
               fea.append((cnt, gib.calc(i)))
               cnt += 1
        return fea
