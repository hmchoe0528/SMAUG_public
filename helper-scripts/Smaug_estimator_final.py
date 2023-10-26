from nd import NoiseDistribution, stddevf
from lwe_parameters import LWEParameters
from lwe import estimate
from reduction import *
import math
from Meet_LWE import meet_lwe
from smaug_dfp_compression import runSmaugError


# run_estimator = 0 (don't run), 1 (lwe only), 2 (lwr only) or 3 (both)
def expSmaugParams(n, k, q, p, T, hs, hr, sigma = 1.0625, run_estimator = 0, run_meet_lwe = True, run_dfp = True, tag = "SmaugExp"):
    
    ############
    # Core-SVP #
    ############
    if run_estimator > 0:
        red_cost_models = [MATZOV("classical"), ADPS16("classical"), ADPS16("quantum")]
        model_names     = ["MATZOV_classical", "ADPS16_classical", " ADPS16_quantum "]
    
        list_attack = ['arora-gb', 'bkw', 'usvp', 'bdd', 'bdd_hybrid', 'bdd_mitm_hybrid', 'dual', 'dual_hybrid']
        
        Smaug_LWE = LWEParameters(n=n*k,
                q=q,
                Xs=NoiseDistribution.SparseTernary(n*k, int(hs / 2), int(hs / 2)),
                Xe=NoiseDistribution.DiscreteGaussian(sigma),
                m=n*k,
                tag="LWE",
                )
        
        Smaug_LWR = LWEParameters(n=n*k,
                q=q,
                Xs=NoiseDistribution.SparseTernary(n*k, int(hr / 2), int(hr / 2)),
                Xe=NoiseDistribution.UniformMod(int(q / p)),
                m=n*k,
                tag="LWR",
                )
        
        core_svp_list = []
        for red_cost_model, model_name in zip(red_cost_models, model_names):
            print("\n"+model_name)
            list_rop = []
            
            # run lwe
            if run_estimator != 2:
                print(f"== {tag}: LWE ==")
                resLWE = estimate(Smaug_LWE, red_cost_model=red_cost_model, jobs=40)
                for x in list_attack:
                    if x in resLWE:
                        list_rop.append(math.log2(resLWE[x].rop))
            # run lwr
            if run_estimator != 1:
                print(f"== {tag}: LWR ==")
                resLWR = estimate(Smaug_LWR, red_cost_model=red_cost_model, jobs=40)
                for x in list_attack:
                    if x in resLWR:
                        list_rop.append(math.log2(resLWR[x].rop))
            
            core_svp_list.append(min(list_rop))
        
        print("\n" + "="*20 + "\n===   "+tag+"   ===\n" + "="*20 + "\nn="+str(n)+", k="+str(k)+", q="+str(q)+", p="+str(p)+", sigma="+str(sigma)+", hs="+str(hs)+", hr="+str(hr)+"\n"+"=" * 20)
        idx = 0
        print(f"Core-SVP hardness:")
        for model_name in model_names:
            print(f"({model_name}) {core_svp_list[idx]:.1f}")
            idx = idx + 1
    
    if run_estimator ==0:
        print("\n" + "="*20 + "\n===   "+tag+"   ===\n" + "="*20 + "\nn="+str(n)+", k="+str(k)+", q="+str(q)+", p="+str(p)+", sigma="+str(sigma)+", hs="+str(hs)+", hr="+str(hr)+"\n"+"=" * 20)

    ############
    # Meet-LWE #
    ############
    if run_meet_lwe == True:
        meet_lwe_cost = meet_lwe(n*k, q, min(hs, hr))
        print(f"Meet-LWE (Rep-2):  {meet_lwe_cost[0]:.1f}, mem: {meet_lwe_cost[3]:.1f}")

    #######
    # DFP #
    #######
    if run_dfp == True:  
        if sigma == 1.0625:
            error = runSmaugError(tag, n, k, q, p, T, hs, hr, {0: 403163305, 1: 258898250, 2: 68560420, 3: 7487107, 4: 337172, 5: 6262, 6: 48})
        elif sigma == 1.453713:
            error = runSmaugError(tag, n, k, q, p, T, hs, hr, {0: 8993, 1: 7098, 2: 3490, 3: 1069, 4: 204, 5: 24, 6: 2})
        else: # sigma = 2.626488
            error = runSmaugError(tag, n, k, q, p, T, hs, hr, {0: 4977, 1: 4629, 2: 3725, 3: 2592, 4: 1561, 5: 813, 6: 366, 7: 143, 8: 48, 9: 14, 10: 4, 11: 1})

        print(f"Decryption failure prob: 2^{error:.1f}")
    
    ########
    # SIZE #
    ########
    print(f"Sizes: pk={32+n*k*math.log(q, 2)/8:.0f}, ctxt={n*(k*math.log(p, 2)+math.log(T, 2))/8:.0f}, sk={16*math.ceil(hs/16)+32} bytes")
    print("=" * 20)

# experiment
#expSmaugParams(256, 2, 1024, 256, 16, 140, 132, run_estimator=3, tag = "expSmaug128")
#expSmaugParams(256, 3, 2048, 256, 128, 198, 151, sigma=1.453713, run_estimator=3, run_meet_lwe=True, tag = "expSmaug192-128")
#expSmaugParams(256, 3, 2048, 256, 64, 198, 151, sigma=1.453713, run_estimator=3, run_meet_lwe=True, tag = "expSmaug192-64")
expSmaugParams(256, 3, 2048, 256, 32, 198, 151, sigma=1.453713, run_estimator=0, run_meet_lwe=True, tag = "expSmaug192-32")
#expSmaugParams(256, 5, 2048, 256, 32, 176, 160, run_estimator=3, run_meet_lwe=True, tag = "expSmaug256")

# Smaug128
#expSmaugParams(256, 2, 1024, 256, 32, 140, 132, run_estimator=3, run_meet_lwe=True, tag = "Smaug128")

# Samug192
#expSmaugParams(256, 3, 2048, 256, 256, 198, 151, sigma=1.453713, run_estimator=3, run_meet_lwe=True, tag = "Smaug192")

# Smaug256
#expSmaugParams(256, 5, 2048, 256, 64, 176, 160, run_estimator=3, run_meet_lwe=True, tag = "Smaug256")
