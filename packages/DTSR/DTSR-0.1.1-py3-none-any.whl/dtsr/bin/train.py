import argparse
import os
import sys
import pickle
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

from dtsr.kwargs import DTSR_INITIALIZATION_KWARGS, DTSRMLE_INITIALIZATION_KWARGS, DTSRBAYES_INITIALIZATION_KWARGS
from dtsr.config import Config
from dtsr.io import read_data
from dtsr.formula import Formula
from dtsr.data import preprocess_data, compute_splitID, compute_partition
from dtsr.util import mse, mae

if __name__ == '__main__':

    argparser = argparse.ArgumentParser('''
        Trains model(s) from formula string(s) given data.
    ''')
    argparser.add_argument('config_path', help='Path to configuration (*.ini) file')
    argparser.add_argument('-m', '--models', nargs='*', default = [], help='Path to configuration (*.ini) file')
    args, unknown = argparser.parse_known_args()

    p = Config(args.config_path)

    if not p.use_gpu_if_available:
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

    if len(args.models) > 0:
        models = args.models
    else:
        models = p.model_list[:]

    run_baseline = False
    run_dtsr = False
    for m in models:
        if not run_baseline and m.startswith('LM') or m.startswith('GAM'):
            run_baseline = True
        elif not run_dtsr and m.startswith('DTSR'):
            run_dtsr = True

    dtsr_formula_list = [Formula(p.models[m]['formula']) for m in p.model_list if m.startswith('DTSR')]
    dtsr_formula_name_list = [m for m in p.model_list if m.startswith('DTSR')]
    all_rangf = [v for x in dtsr_formula_list for v in x.rangf]
    X, y = read_data(p.X_train, p.y_train, p.series_ids, categorical_columns=list(set(p.split_ids + p.series_ids + [v for x in dtsr_formula_list for v in x.rangf])))
    X, y, select, X_2d_predictor_names, X_2d_predictors = preprocess_data(
        X,
        y,
        p,
        dtsr_formula_list,
        compute_history=run_dtsr
    )

    if run_baseline:
        X['splitID'] = compute_splitID(X, p.split_ids)
        part = compute_partition(X, p.modulus, 3)
        part_select = part[0]
        X_baseline = X[part_select]
        X_baseline = X_baseline.reset_index(drop=True)[select]

    n_train_sample = len(y)

    for i in range(len(dtsr_formula_list)):
        x = dtsr_formula_list[i]
        if run_baseline and x.dv not in X_baseline.columns:
            X_baseline[x.dv] = y[x.dv]

    if run_baseline:
        from dtsr.baselines import py2ri
        for c in X_baseline.columns:
            if X_baseline[c].dtype.name == 'category':
                X_baseline[c] = X_baseline[c].astype(str)
        X_baseline = py2ri(X_baseline)

    for m in models:
        p.set_model(m)
        formula = p['formula']
        if not os.path.exists(p.outdir + '/' + m):
            os.makedirs(p.outdir + '/' + m)
        if m.startswith('LME'):
            from dtsr.baselines import LME

            dv = formula.strip().split('~')[0].strip().replace('.','')

            if os.path.exists(p.outdir + '/' + m + '/m.obj'):
                sys.stderr.write('Retrieving saved model %s...\n' % m)
                with open(p.outdir + '/' + m + '/m.obj', 'rb') as m_file:
                    lme = pickle.load(m_file)
            else:
                sys.stderr.write('Fitting model %s...\n' % m)
                lme = LME(formula, X_baseline)
                with open(p.outdir + '/' + m + '/m.obj', 'wb') as m_file:
                    pickle.dump(lme, m_file)

            lme_preds = lme.predict(X_baseline)
            lme_mse = mse(y[dv], lme_preds)
            lme_mae = mae(y[dv], lme_preds)
            summary = '=' * 50 + '\n'
            summary += 'LME regression\n\n'
            summary += 'Model name: %s\n\n' %m
            summary += 'Formula:\n'
            summary += '  ' + formula + '\n'
            summary += str(lme.summary()) + '\n'
            summary += 'Training set loss:\n'
            summary += '  MSE: %.4f\n' % lme_mse
            summary += '  MAE: %.4f\n' % lme_mae
            summary += '=' * 50 + '\n'
            with open(p.outdir + '/' + m + '/summary.txt', 'w') as f_out:
                f_out.write(summary)
            sys.stderr.write(summary)
            sys.stderr.write('\n\n')

        elif m.startswith('LM'):
            from dtsr.baselines import LM

            dv = formula.strip().split('~')[0].strip().replace('.','')

            if os.path.exists(p.outdir + '/' + m + '/m.obj'):
                sys.stderr.write('Retrieving saved model %s...\n' % m)
                with open(p.outdir + '/' + m + '/m.obj', 'rb') as m_file:
                    lm = pickle.load(m_file)
            else:
                sys.stderr.write('Fitting model %s...\n' % m)
                lm = LM(formula, X_baseline)
                with open(p.outdir + '/' + m + '/m.obj', 'wb') as m_file:
                    pickle.dump(lm, m_file)

            lm_preds = lm.predict(X_baseline)
            lm_mse = mse(y[dv], lm_preds)
            lm_mae = mae(y[dv], lm_preds)
            summary = '=' * 50 + '\n'
            summary += 'Linear regression\n\n'
            summary += 'Model name: %s\n\n' %m
            summary += 'Formula:\n'
            summary += '  ' + formula + '\n'
            summary += str(lm.summary()) + '\n'
            summary += 'Training set loss:\n'
            summary += '  MSE: %.4f\n' % lm_mse
            summary += '  MAE: %.4f\n' % lm_mae
            summary += '=' * 50 + '\n'
            with open(p.outdir + '/' + m + '/summary.txt', 'w') as f_out:
                f_out.write(summary)
            sys.stderr.write(summary)
            sys.stderr.write('\n\n')

        elif m.startswith('GAM'):
            import re
            from dtsr.baselines import GAM

            dv = formula.strip().split('~')[0].strip().replace('.','')
            ran_gf = ['subject', 'word', 'sentid']

            ## For some reason, GAM can't predict using custom functions, so we have to translate them
            z_term = re.compile('z.\((.*)\)')
            c_term = re.compile('c.\((.*)\)')
            formula = [t.strip() for t in formula.strip().split() if t.strip() != '']
            for i in range(len(formula)):
                formula[i] = z_term.sub(r'scale(\1)', formula[i])
                formula[i] = c_term.sub(r'scale(\1, scale=FALSE)', formula[i])
            formula = ' '.join(formula)

            if os.path.exists(p.outdir + '/' + m + '/m.obj'):
                sys.stderr.write('Retrieving saved model %s...\n' % m)
                with open(p.outdir + '/' + m + '/m.obj', 'rb') as m_file:
                    gam = pickle.load(m_file)
            else:
                sys.stderr.write('Fitting model %s...\n' % m)
                gam = GAM(formula, X_baseline, ran_gf=ran_gf)
                with open(p.outdir + '/' + m + '/m.obj', 'wb') as m_file:
                    pickle.dump(gam, m_file)

            gam_preds = gam.predict(X_baseline)
            gam_mse = mse(y[dv], gam_preds)
            gam_mae = mae(y[dv], gam_preds)
            summary = '=' * 50 + '\n'
            summary += 'GAM regression\n\n'
            summary += 'Model name: %s\n\n' %m
            summary += 'Formula:\n'
            summary += '  ' + formula + '\n'
            summary += str(gam.summary()) + '\n'
            summary += 'Training set loss:\n'
            summary += '  MSE: %.4f\n' % gam_mse
            summary += '  MAE: %.4f\n' % gam_mae
            summary += '=' * 50 + '\n'
            with open(p.outdir + '/' + m + '/summary.txt', 'w') as f_out:
                f_out.write(summary)
            sys.stderr.write(summary)
            sys.stderr.write('\n\n')

        elif m.startswith('DTSR'):
            dv = formula.strip().split('~')[0].strip()
            y_complete_cases = y[np.isfinite(y[dv])]

            sys.stderr.write('\nInitializing model %s...\n\n' % m)

            if p['network_type'] in ['mle', 'nn']:
                bayes = False
            else:
                bayes = True

            kwargs = {}
            for kwarg in DTSR_INITIALIZATION_KWARGS:
                if kwarg.key not in ['outdir', 'history_length']:
                    kwargs[kwarg.key] = p[kwarg.key]

            if p['network_type'] in ['mle', 'nn']:
                from dtsr.dtsrmle import DTSRMLE

                for kwarg in DTSRMLE_INITIALIZATION_KWARGS:
                    kwargs[kwarg.key] = p[kwarg.key]

                dtsr_model = DTSRMLE(
                    formula,
                    X,
                    y_complete_cases,
                    outdir=p.outdir + '/' + m,
                    history_length=p.history_length,
                    **kwargs
                )
            elif p['network_type'].startswith('bayes'):
                from dtsr.dtsrbayes import DTSRBayes

                for kwarg in DTSRBAYES_INITIALIZATION_KWARGS:
                    kwargs[kwarg.key] = p[kwarg.key]

                dtsr_model = DTSRBayes(
                    formula,
                    X,
                    y_complete_cases,
                    outdir=p.outdir + '/' + m,
                    history_length=p.history_length,
                    **kwargs
                )
            else:
                raise ValueError('Network type "%s" not supported' %p['network_type'])

            sys.stderr.write('\nFitting model %s...\n\n' % m)

            dtsr_model.fit(
                X,
                y_complete_cases,
                n_iter=p['n_iter'],
                X_2d_predictor_names=X_2d_predictor_names,
                X_2d_predictors=X_2d_predictors,
                irf_name_map=p.irf_name_map,
                plot_n_time_units=p['plot_n_time_units'],
                plot_n_points_per_time_unit=p['plot_n_points_per_time_unit'],
                plot_x_inches=p['plot_x_inches'],
                plot_y_inches=p['plot_y_inches'],
                cmap=p['cmap']
            )

            dtsr_preds = dtsr_model.predict(
                X,
                y_complete_cases.time,
                y_complete_cases[dtsr_model.form.rangf],
                y_complete_cases.first_obs,
                y_complete_cases.last_obs,
                X_2d_predictor_names=X_2d_predictor_names,
                X_2d_predictors=X_2d_predictors,
            )

            dtsr_mse = mse(y_complete_cases[dv], dtsr_preds)
            dtsr_mae = mae(y_complete_cases[dv], dtsr_preds)
            y_dv_mean = y_complete_cases[dv].mean()

            summary = '*' * 50 + '\n\n'
            summary = '=' * 50 + '\n'
            summary += 'DTSR regression\n\n'
            summary = '=' * 50 + '\n'
            summary += 'MODEL NAME:\n'
            summary +=  '  % s\n\n' % m

            summary += dtsr_model.report_initialization_overview()

            dtsr_loglik_vector = dtsr_model.log_lik(
                X,
                y_complete_cases,
                X_2d_predictor_names=X_2d_predictor_names,
                X_2d_predictors=X_2d_predictors,
            )
            dtsr_loglik = dtsr_loglik_vector.sum()
            summary += 'Log likelihood: %s\n' %dtsr_loglik

            if bayes:
                if dtsr_model.pc:
                    terminal_names = dtsr_model.src_terminal_names
                else:
                    terminal_names = dtsr_model.terminal_names
                posterior_summaries = np.zeros((len(terminal_names), 3))
                for i in range(len(terminal_names)):
                    terminal = terminal_names[i]
                    row = np.array(dtsr_model.ci_integral(terminal, n_time_units=10))
                    posterior_summaries[i] += row
                posterior_summaries = pd.DataFrame(posterior_summaries, index=terminal_names, columns=['Mean', '2.5%', '97.5%'])

                summary += '\nPOSTERIOR INTEGRAL SUMMARIES BY PREDICTOR:\n'
                summary += posterior_summaries.to_string() + '\n\n'

            summary += 'TRAINING SET EVALUATION:\n'
            summary += '  MSE: %.4f\n' % dtsr_mse
            summary += '  MAE: %.4f\n' % dtsr_mae
            summary += '=' * 50 + '\n'

            with open(p.outdir + '/' + m + '/summary.txt', 'w') as f_out:
                f_out.write(summary)
            sys.stderr.write(summary)
            sys.stderr.write('\n\n')

            dtsr_model.finalize()

