var thal = function(oligo_f, oligo_r, options) {
    var length_3;
    var duplex_init_H, duplex_init_S;
    var RC;

    var oligo_1 = oligo_f;
    var oligo_2 = oligo_r;
    var oligo_2_rev;
    var num_seq_1 = new Uint8Array(oligo_1.length + 2);
    var num_seq_2 = new Uint8Array(oligo_2.length + 2);

    var output = {};

    if (options['type'] === 4) {
        length_3 = oligo_2.length - 1;
        duplex_init_H = 0.0;
        duplex_init_S = -0.00000000001;
        RC = 0;
    } else {
        /* hybridization of two oligos */
        duplex_init_H = 200;
        duplex_init_S = -5.7;
        if(symmetry_thermo(oligo_1) && symmetry_thermo(oligo_2)) {
          RC = R  * Math.log(options['dna_conc'] / 1000000000.0);
        } else {
          RC = R  * Math.log(options['dna_conc'] / 4000000000.0);
        }
        if (options['type'] != 3) {
            oligo_2_rev = seqstr.s_revSeq(oligo_r);
        } else {
            oligo_2_rev = seqstr.s_revSeq(oligo_f);
        }
    }
    for(var i = 1; i <= oligo_1.length; ++i) {
        num_seq_1[i] = str2int(oligo_1[i - 1]);
    }
    for(var i = 1; i <=  oligo_2.length; ++i) {
        num_seq_2[i] = str2int(oligo_2[i - 1]);
    }
    // mark as N-s
    num_seq_1[0] = num_seq_1[oligo_1.length + 1] = 4;
    num_seq_2[0] = num_seq_2[oligo_2.length + 1] = 4;

    if (options['type'] === 4) {  // calculate structure of monomer
        enthalpy_DPT = new Float64Array(oligo_1.length*oligo_2.length);
        entropy_DPT = new Float64Array(oligo_1.length*oligo_2.length);
        initMatrix2();
        fillMatrix2(options['max_loop']);
        calc_terminal_bp(option['temp']);
        mh = HEND5(oligo_1.length);
        ms = SEND5(oligo_1.length);
        options['align_end_1'] = mh;
        options['align_end_2'] = ms;
        bp = new Int32Array(oligo_1.length);}
        if(isFinite(mh)) {
            tracebacku(bp, a['max_loop'], output);
        } else if (options['temponly'] === 0) {
            output.no_structure = 1;
        }
        if(output.temp == -_INFINITY ) {
            output.temp = 0.0;
        }

    } else { // hybridization of two molecules
        length_3 = oligo_2.length;
        enthalpy_DPT = new Float64Array(oligo_1.length*oligo_2.length); /* dyn. programming table for dS and dH */
        entropy_DPT = new Float64Array(oligo_1.length*oligo_2.length);  /* enthalpyDPT is 3D array represented as 1D array */
        initMatrix();
        fillMatrix(options['max_loop']);
        var SH_left = -_INFINITY;
        var SH = new Float64Array(2);
        /* calculate terminal basepairs */
        best_I = best_J = 0;
        if (options['type'] === 1) {
            for (var i = 1; i <= oligo_1.length; i++) {
                for (var j = 1; j <= oligo_2.length; j++) {
                    RSH(i, j, SH);
                    SH[0] = SH[0] + SMALL_NON_ZERO; /* this adding is done for compiler, optimization -O2 vs -O0 */
                    SH[1] = SH[1] + SMALL_NON_ZERO;
                    T1 = ((EnthalpyDPT(i, j)+ SH[1] + dplx_init_H) / ((EntropyDPT(i, j)) + SH[0] +
                          dplx_init_S + RC)) - ABSOLUTE_ZERO;
                    if (T1 > SH_left  && ((EntropyDPT(i, j) + SH[0]) < 0 && (SH[1] + EnthalpyDPT(i, j)) < 0)) {
                        SH_left = T1;
                        best_I = i;
                        best_J = j;
                    }
                }
            }
        }
        ps_1 = new Int32Array(oligo_1.length);
        ps_2 = new Int32Array(oligo_2.length);
        if ((options['type'] === 2) || (options['type'] === 3)) {
            /* THAL_END1 */
            best_I = best_J = 0;
            best_I = oligo_1.length;
            var i = oligo_1.length;
            SH_left = -_INFINITY;
            for (var j = 1; j <= oligo_2.length; ++j) {
                RSH(i, j, SH);
                SH[0] = SH[0] + SMALL_NON_ZERO; /* this adding is done for compiler, optimization -O2 vs -O0,
                                               that compiler could understand that SH is changed in this cycle */
                SH[1] = SH[1] + SMALL_NON_ZERO;
                T1 = ((EnthalpyDPT(i, j)+ SH[1] + dplx_init_H) / ((EntropyDPT(i, j)) + SH[0] +
                    dplx_init_S + RC)) - ABSOLUTE_ZERO;
                if (T1 > SH_left && ((SH[0] + EntropyDPT(i, j)) < 0 && (SH[1] + EnthalpyDPT(i, j)) < 0)) {
                    SH_left = T1;
                    bestJ = j;
                }
            }
        }
        if (!isFinite(SH_left)) { best_I = best_J = 1; }
            RSH(bestI, bestJ, SH);
            dH = EnthalpyDPT(best_I, best_J)+ SH[1] + duplex_init_H;
            dS = EntropyDPT(best_I, best_J) + SH[0] + duplex_init_S;
            /* tracebacking */
            for (var i = 0; i < oligo_1.length; ++i) {
                ps_1[i] = 0;
            }
            for (var j = 0; j < oligo_2.length; ++j) {
                ps_2[j] = 0;
            }
            if (isFinite(EnthalpyDPT(best_I, best_J))) {
                traceback(bestI, bestJ, RC, ps_1, ps_2, options['max_loop'], output);
                if (print_output) {
                    drawDimer(ps_1, ps_2, SH_left, dH, dS,
                        options['temponly'], options['temp'], output);
                } else {
                    calcDimer(ps_1, ps_2, SH_left, dH, dS, 
                        options['temponly'], options['temp'], output);
                }
                output.align_end_1 = best_I;
                output.align_end_2 = best_J;
            } else {
                output.no_structure = 1;
                output.temp = 0.0;
            }
        }
        return;
    }
}