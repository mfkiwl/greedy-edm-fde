"""Reproduce figures for presentation.

"""

__authors__ = "D. Knowles"
__date__ = "16 Aug 2023"

import os
from datetime import datetime, timezone

import numpy as np
from sklearn import metrics as sk
import matplotlib.pyplot as plt
import gnss_lib_py as glp
from gnss_lib_py.algorithms.fde import _edm_from_satellites_ranges
from gnss_lib_py.visualizations.style import save_figure
from gnss_lib_py.visualizations.plot_metric import  _get_new_fig

np.random.seed(314)

locations = {
              "calgary" : 10,
              "cape_town" : 6,
              "hong_kong" : 1,
              "london" : 21,
              "munich" : 10,
              "sao_paulo" : 17,
              "stanford_oval" : 10,
              "sydney" : 11,
              "zurich" : 2,
             }

def main():

    # update results directory and result file name here
    simulated_results_dir = os.path.join(os.getcwd(),"results","<simulated results directory>")
    simulated_results_path = os.path.join(simulated_results_dir,"fde_<simulated #>_navdata.csv")

    gsdc_dir = os.path.join(os.getcwd(),"results","<gsdc results directory>")
    gsdc_state_path = os.path.join(gsdc_dir,"fde_state_<gsdc #>_navdata.csv")
    gsdc_timing_path = os.path.join(gsdc_dir,"fde_<gsdc #>_navdata.csv")

    # timing plots
    print("timing plots")
    timing_plots_calculations(simulated_results_path)
    timing_plots(simulated_results_dir)

    print("eigenvalue plots")
    # without measurement noise
    moving_eigenvalues(noise=False)
    # with measurement noise
    moving_eigenvalues(noise=True)

    # singular value U matrix
    print("singular value plot")
    moving_svd(noise=False)

    # skyplots from simulated data
    # world_skyplots_check()
    print("skykplots")
    world_skyplots()

    print("satellites in view")
    plot_sats_in_view()

    #accuracy plots
    # accuracy_plots(simulated_results_path)

    # roc curve
    print("roc curve")
    roc_curve(simulated_results_path)
    print("auc table")
    auc_table(simulated_results_path)

    # gsdc error plots
    gsdc_error(gsdc_state_path)

    # gsdc timing plots
    gsdc_timing_plots_calculations(gsdc_timing_path)
    gsdc_timing_plots(gsdc_dir)

    plt.show()

def create_label(items):
    """Custom label combinations for navdata.

    Parameters
    ----------
    items : list
        Items to combine.

    Returns
    -------
    label : string
        Label to use for combined data.

    """

    if len(items) == 1:
        return items
    label = items[0]
    for l_index in range(1,len(items)):
        label = np.char.add(label,"_")
        label = np.char.add(label,items[l_index])

    return label

def gsdc_error(gsdc_results_path):
    """Plot the state error.

    Parameters
    ----------
    gsdc_results_path : string
        Paths to saved state metrics.

    """


    navdata = glp.NavData(csv_path = gsdc_results_path)
    navdata["threshold2"] = np.nan_to_num(navdata["threshold"])

    all_score = np.mean(navdata.where("method","all").where("horizontal_50_95",300,"leq")["horizontal_50_95"])
    nonfaulty_score = np.mean(navdata.where("method","gt_nonfaulty").where("horizontal_50_95",300,"leq")["horizontal_50_95"])
    min_edm = np.mean(navdata.where("method","edm").where("threshold",0.55)["horizontal_50_95"])
    min_edm_2021 = np.mean(navdata.where("method","edm_2021").where("threshold",3)["horizontal_50_95"])
    min_residual = np.mean(navdata.where("method","residual").where("threshold",300)["horizontal_50_95"])

    fig = glp.plot_metric(navdata.where("method","edm").where("threshold",(0.40,0.7),"neq"),
                          "threshold",
                          "horizontal_50_95",
                           groupby="method",
                           linestyle="none",
                           avg_y = True,
                           save=True,
                           markersize=10,
                           color="C0",
                           zorder=9,
                           title="MEAN OF 50th & 95th PERCENTILE ERRORS",
                          )
    plt.plot([0,1],[min_residual,min_residual],
            linewidth=3.0,
            linestyle="solid",
            marker=",",
            markersize=0,
            label="RESIDUAL MINIMUM",
            color="C1"
            )
    plt.plot([0,1],[min_edm_2021,min_edm_2021],
            linewidth=3.0,
            linestyle="dashed",
            marker=",",
            markersize=0,
            label="EDM 2021 MINIMUM",
            color="C2"
            )
    plt.plot([0.,1.],[all_score,all_score],
            linewidth=3.0,
            linestyle="dotted",
            marker=",",
            markersize=0,
            color="C3",
            label="ALL MEASUREMENTS",
            )
    plt.plot([0.,1.],[nonfaulty_score,nonfaulty_score],
            linewidth=3.0,
            linestyle="dashdot",
            marker=",",
            markersize=0,
            color="C4",
            label='"MULTIPATH" REMOVED',
            )

    plt.ylim(4,12)
    plt.xlim(0.40,0.7)
    plt.ylabel("HORIZONTAL DISTANCE ERROR")
    plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1),
                   title="METHOD")
    fig.set_layout_engine(layout="tight")
    save_figure(fig,"gsdc_edm_error")


    fig = plt.figure()
    plt.plot([0.1,10E6],[min_edm,min_edm],
            linewidth=3.0,
            linestyle="dashed",
            marker=",",
            markersize=0,
            label="EDM MINIMUM",
            color="C0"
            )
    fig = glp.plot_metric(navdata.where("method","residual"),
                          "threshold",
                          "horizontal_50_95",
                           groupby="method",
                           linestyle="none",
                           avg_y = True,
                           save=True,
                           color="C1",
                           marker="*",
                           markersize=10,
                           fig=fig,
                           zorder=9,
                           title="MEAN OF 50th & 95th PERCENTILE ERRORS",
                          )
    plt.plot([0.1,10E6],[min_edm_2021,min_edm_2021],
            linewidth=3.0,
            linestyle="solid",
            marker=",",
            markersize=0,
            label="EDM 2021 MINIMUM",
            color="C2"
            )
    plt.plot([0.1,10E6],[all_score,all_score],
            linewidth=3.0,
            linestyle="dotted",
            marker=",",
            markersize=0,
            label="ALL MEASUREMENTS",
            color="C3"
            )
    plt.plot([0.1,10E6],[nonfaulty_score,nonfaulty_score],
            linewidth=3.0,
            linestyle="dashdot",
            marker=",",
            markersize=0,
            label='"MULTIPATH" REMOVED',
            color="C4"
            )

    plt.ylabel("HORIZONTAL DISTANCE ERROR")
    plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1),
                   title="METHOD")

    plt.xscale("log")
    plt.ylim(4,12)
    plt.xlim(3,3E5)
    fig.set_layout_engine(layout="tight")
    save_figure(fig,"gsdc_residual_error")

    fig = plt.figure()
    plt.plot([-100,600],[min_edm,min_edm],
            linewidth=3.0,
            linestyle="dashed",
            marker=",",
            markersize=0,
            label="EDM MINIMUM",
            color="C0"
            )
    plt.plot([-100,600],[min_residual,min_residual],
            linewidth=3.0,
            linestyle="solid",
            marker=",",
            markersize=0,
            label="RESIDUAL MINIMUM",
            color="C1"
            )
    fig = glp.plot_metric(navdata.where("method","edm_2021"),
                          "threshold",
                          "horizontal_50_95",
                           groupby="method",
                           linestyle="none",
                           avg_y = True,
                           save=True,
                           color="C2",
                           marker="P",
                           markersize=10,
                           fig = fig,
                           zorder=9,
                           title="MEAN OF 50th & 95th PERCENTILE ERRORS",
                          )
    plt.plot([-100,600],[all_score,all_score],
            linewidth=3.0,
            linestyle="dotted",
            marker=",",
            markersize=0,
            label="ALL MEASUREMENTS",
            color="C3"
            )
    plt.plot([-100,600],[nonfaulty_score,nonfaulty_score],
            linewidth=3.0,
            linestyle="dashdot",
            marker=",",
            markersize=0,
            label='"MULTIPATH" REMOVED',
            color="C4"
            )

    plt.ylabel("HORIZONTAL DISTANCE ERROR")
    plt.legend(loc="upper left", bbox_to_anchor=(1.05, 1),
                   title="METHOD")

    plt.xscale("log")
    plt.xlim(0.1,500)
    plt.ylim(4,12)
    # plt.xlim(,350)
    # plt.xticks(range(0,300,100))
    fig.set_layout_engine(layout="tight")
    save_figure(fig,"gsdc_edm_2021_error")

def gsdc_timing_plots_calculations(gsdc_results_path):
    """Calculations for the timing plots.

    Parameters
    ----------
    gsdc_results_path : string
        Paths to saved metrics.

    """

    navdata = glp.NavData(csv_path = gsdc_results_path)
    # navdata = navdata.copy(cols=list(range(0,22)))
    navdata["glp_label"] = create_label([
                                         navdata["trace"].astype(str),
                                         navdata["phone"].astype(str),
                                         navdata["method"].astype(str),
                                         ])
    timing_measurements = {}
    methods = ("edm","residual","edm_2021")
    for method in methods:
        timing_measurements[method] = {}

    for glp_label in np.unique(navdata["glp_label"]):
        print("calculating timing for:",glp_label)
        navdata_cropped = navdata.where("glp_label",glp_label)
        row_idx = np.argmin(navdata_cropped["horizontal_50_95"])
        method = navdata_cropped["method",row_idx].item()
        trace = navdata_cropped["trace",row_idx].item()
        phone = navdata_cropped["phone",row_idx].item()
        threshold = navdata_cropped["threshold",row_idx].item()
        if threshold == 0:
            threshold = str(int(threshold)).zfill(4)
        elif threshold < 1:
            threshold = str(np.round(threshold,4)).zfill(4)
        else:
            threshold = str(int(threshold)).zfill(4)

        file_prefix = [method,trace,phone,threshold]
        file_name = "_".join(file_prefix).replace(".","") + "_navdata.csv"
        file_path = os.path.join(os.path.dirname(gsdc_results_path),file_name)
        print("reading path:",file_path)
        navdata_file = glp.NavData(csv_path=file_path)

        for _, _, navdata_subset in glp.loop_time(navdata_file,"gps_millis"):
            compute_time_ms = navdata_subset["compute_time_s",0]*1000
            num_measurements = len(navdata_subset)
            if num_measurements not in timing_measurements[method]:
                timing_measurements[method][num_measurements] = [compute_time_ms]
            else:
                timing_measurements[method][num_measurements].append(compute_time_ms)

    measurements_navdata = glp.NavData()
    for method in methods:
        for k,v in timing_measurements[method].items():
            single_navdata = glp.NavData()
            single_navdata["method"] = np.array([method])
            single_navdata["measurements"] = k
            single_navdata["mean_compute_time_ms"] = np.mean(v)
            single_navdata["min_compute_time_ms"] = np.min(v)
            single_navdata["max_compute_time_ms"] = np.max(v)
            single_navdata["median_compute_time_ms"] = np.median(v)
            single_navdata["std_compute_time_ms"] = np.std(v)
            measurements_navdata = glp.concat(measurements_navdata,single_navdata)

    measurements_navdata.to_csv(output_path=os.path.join(os.path.dirname(gsdc_results_path),
                                                         "gsdc_measurements_timing.csv"))

def gsdc_timing_plots(gsdc_results_dir):
    """Plot the state error.

    Parameters
    ----------
    gsdc_results_path : string
        Paths to saved state metrics.

    """



    measurements_navdata = glp.NavData(csv_path=os.path.join(gsdc_results_dir,"gsdc_measurements_timing.csv"))

    glp.sort(measurements_navdata,"measurements",inplace=True)

    navdata_plot = measurements_navdata.where("measurements",25,"geq").where("measurements",45,"leq")

    fig = plt.figure()

    plt.gca().set_prop_cycle(None)
    for method in ["edm","residual","edm_2021"]:
        navdata_std = navdata_plot.where("method",method)
        fig = glp.plot_metric(navdata_std,
                        "measurements","mean_compute_time_ms",
                        groupby="method",
                        save=False,
                        linewidth=5.0,
                        markersize=10,
                        linestyle="None",
                        fig = fig,
                        )
        if len(navdata_std) > 1:
            plt.fill_between(navdata_std["measurements"],
                             navdata_std["mean_compute_time_ms"] - 1*navdata_std["std_compute_time_ms"],
                             navdata_std["mean_compute_time_ms"] + 1*navdata_std["std_compute_time_ms"],
                             alpha=0.5)
    plt.yscale("log")
    plt.xlim(24,46)
    plt.ylim(0.2,110)
    plt.xticks(range(25,46,5))
    save_figure(fig,"gsdc_measurements_mean_compute_time_ms")

def roc_curve(simulated_results_path):
    """Plot the ROC curve.

    Parameters
    ----------
    simulated_results_path : string
        Paths to saved metrics.

    """

    navdata = glp.NavData(csv_path = simulated_results_path)
    navdata["method_and_bias_m"] = np.char.add(np.char.add(navdata["method"].astype(str),"_"),
                                                navdata["bias"].astype(str))
    navdata.rename({"far":"false_alarm_rate","tpr":"true_positive_rate"},inplace=True)
    navdata["glp_label"] = create_label([
                                         navdata["faults"].astype(str),
                                         navdata["location_name"].astype(str),
                                        ])

    for glp_label in ["8_munich"]:

        fig = glp.plot_metric(navdata.where("glp_label",glp_label).where("method","edm"),
                        "false_alarm_rate","true_positive_rate",
                        groupby="method_and_bias_m",
                        save=False,
                        avg_y=True,
                        linewidth=3.0,
                        markersize=6,
                        )

        plt.gca().set_prop_cycle(None)
        glp.plot_metric(navdata.where("glp_label",glp_label).where("method","residual"),
                        "false_alarm_rate","true_positive_rate",
                        groupby="method_and_bias_m",
                        avg_y=True,
                        save=True,
                        title="",
                        prefix="roc_curve",
                        linewidth=3.0,
                        markersize=6,
                        linestyle="dotted",
                        fig=fig,
                        )
        # plt.gca().set_prop_cycle(None)
        # glp.plot_metric(navdata.where("glp_label",glp_label).where("method","edm_2021"),
        #                 "false_alarm_rate","true_positive_rate",
        #                 groupby="method_and_bias_m",
        #                 avg_y=True,
        #                 save=True,
        #                 title="",
        #                 prefix="roc_curve",
        #                 linewidth=3.0,
        #                 markersize=6,
        #                 linestyle="--",
        #                 fig=fig,
        #                 )
        plt.xlim(0.0,0.9)
        plt.ylim(0.0,1.0)

def auc_table(simulated_results_path):
    """Create the AUC table.

    Parameters
    ----------
    simulated_results_path : string
        Paths to saved metrics.

    """

    navdata = glp.NavData(csv_path = simulated_results_path)
    navdata_cropped = glp.concat(navdata.where("bias",60).where("faults",12),navdata.where("bias",10).where("faults",1))

    navdata_cropped["glp_label"] = create_label([navdata_cropped["bias"].astype(str),
                                                 navdata_cropped["faults"].astype(str),
                                                 navdata_cropped["location_name"].astype(str),
                                                 ])
    navdata_auc = glp.NavData()
    for glp_label in np.unique(navdata_cropped["glp_label"]):
        navdata_method_bias = navdata_cropped.where("glp_label",glp_label)

        label_navdata = glp.NavData()
        label_navdata["location_name"] = np.array([navdata_method_bias["location_name",0]])
        label_navdata["bias"] = np.array([navdata_method_bias["bias",0]])
        label_navdata["faults"] = np.array([navdata_method_bias["faults",0]])

        for method in np.unique(navdata_cropped["method"]):
            far = navdata_method_bias.where("method",method)["far"]
            tpr = navdata_method_bias.where("method",method)["tpr"]
            far_sort = np.argsort(far)
            far = far[far_sort]
            tpr = tpr[far_sort]
            if min(far) < 0.7 and max(far) > 0.7:
                interp_value = 0.7
                interp_point = np.interp(0.7,far,tpr)

                tpr = tpr[far<interp_value].tolist() + [interp_point]
                far = far[far<interp_value].tolist() + [interp_value]

            auc = sk.auc(far,tpr)


            label_navdata[method + "_auc"] = np.round(auc,2)

        navdata_auc = glp.concat(navdata_auc,label_navdata)

    navdata_auc.to_csv(prefix="auc_latex",sep="&",lineterminator="\\\\\n")
    navdata_auc.to_csv(prefix="auc")

    navdata_auc["edm_wins"] = navdata_auc["edm_auc"] > navdata_auc["residual_auc"]
    print(navdata_auc)

def timing_plots_calculations(simulated_results_path):
    """Calculations for the timing plots.

    Parameters
    ----------
    simulated_results_path : string
        Paths to saved metrics.

    """

    navdata = glp.NavData(csv_path = simulated_results_path)
    navdata["glp_label"] = create_label([navdata["faults"].astype(str),
                                         navdata["bias"].astype(str),
                                         navdata["location_name"].astype(str),
                                         navdata["method"].astype(str),
                                         ])
    timing_measurements = {}
    timing_faults = {}
    # methods = ("edm","residual","edm_2021")
    methods = ("edm","residual")
    for method in methods:
        timing_faults[method] = {}
        timing_measurements[method] = {}

    for glp_label in np.unique(navdata["glp_label"]):
        print("calculating timing for:",glp_label)
        navdata_cropped = navdata.where("glp_label",glp_label)
        row_idx = np.argmax(navdata_cropped["balanced_accuracy"])
        method = navdata_cropped["method",row_idx].item()
        location_name = navdata_cropped["location_name",row_idx].item()
        faults = navdata_cropped["faults",row_idx].item()
        bias = navdata_cropped["bias",row_idx].item()
        threshold = navdata_cropped["threshold",row_idx].item()
        if threshold == 0:
            threshold = str(int(threshold)).zfill(4)
        elif threshold < 1:
            threshold = str(np.round(threshold,4)).zfill(4)
        else:
            threshold = str(int(threshold)).zfill(4)

        file_prefix = [method,location_name,str(faults),str(bias),
                       threshold]
        file_name = "_".join(file_prefix).replace(".","") + "_navdata.csv"
        file_path = os.path.join(os.path.dirname(simulated_results_path),file_name)
        navdata_file = glp.NavData(csv_path=file_path)

        for _, _, navdata_subset in glp.loop_time(navdata_file,"gps_millis"):
            compute_time_ms = navdata_subset["compute_time_s",0]*1000
            faults = np.sum(navdata_subset["fault_gt"])
            if faults not in [1,2,4,8,12]:
                continue
            num_measurements = len(navdata_subset)

            if faults not in timing_faults[method]:
                timing_faults[method][faults] = [compute_time_ms]
            else:
                timing_faults[method][faults].append(compute_time_ms)

            if num_measurements not in timing_measurements[method]:
                timing_measurements[method][num_measurements] = [compute_time_ms]
            else:
                timing_measurements[method][num_measurements].append(compute_time_ms)


    faults_navdata = glp.NavData()
    measurements_navdata = glp.NavData()
    for method in methods:
        for k,v in timing_faults[method].items():
            single_navdata = glp.NavData()
            single_navdata["method"] = np.array([method])
            single_navdata["faults"] = k
            single_navdata["mean_compute_time_ms"] = np.mean(v)
            single_navdata["min_compute_time_ms"] = np.min(v)
            single_navdata["max_compute_time_ms"] = np.max(v)
            single_navdata["median_compute_time_ms"] = np.median(v)
            single_navdata["std_compute_time_ms"] = np.std(v)
            faults_navdata = glp.concat(faults_navdata,single_navdata)
        for k,v in timing_measurements[method].items():
            single_navdata = glp.NavData()
            single_navdata["method"] = np.array([method])
            single_navdata["measurements"] = k
            single_navdata["mean_compute_time_ms"] = np.mean(v)
            single_navdata["min_compute_time_ms"] = np.min(v)
            single_navdata["max_compute_time_ms"] = np.max(v)
            single_navdata["median_compute_time_ms"] = np.median(v)
            single_navdata["std_compute_time_ms"] = np.std(v)
            measurements_navdata = glp.concat(measurements_navdata,single_navdata)

    measurements_navdata.to_csv(output_path=os.path.join(os.path.dirname(simulated_results_path),
                                                         "measurements_timing.csv"))
    faults_navdata.to_csv(output_path=os.path.join(os.path.dirname(simulated_results_path),
                                                         "faults_timing.csv"))

def timing_plots(simulated_results_dir):
    """Plot timing info.

    Parameters
    ----------
    simulated_results_dir : string
        Directory to saved metrics.

    """

    faults_navdata = glp.NavData(csv_path=os.path.join(simulated_results_dir,"faults_timing.csv"))
    measurements_navdata = glp.NavData(csv_path=os.path.join(simulated_results_dir,"measurements_timing.csv"))

    glp.sort(faults_navdata,"faults",inplace=True)
    glp.sort(measurements_navdata,"measurements",inplace=True)

    for graph_type in ["faults","measurements"]:
        if graph_type == "faults":
            navdata_plot = faults_navdata
        else:
            navdata_plot = measurements_navdata

        fig = glp.plot_metric(navdata_plot,
                        graph_type,"mean_compute_time_ms",
                        groupby="method",
                        save=False,
                        linewidth=5.0,
                        markersize=10,
                        linestyle="None",
                        )

        plt.gca().set_prop_cycle(None)
        # for method in ["edm","edm_2021","residual"]:
        for method in ["edm","residual"]:
            navdata_std = navdata_plot.where("method",method)
            # print(navdata_std[graph_type])
            if len(navdata_std) > 1:
                plt.fill_between(navdata_std[graph_type],
                                 navdata_std["mean_compute_time_ms"] - 1*navdata_std["std_compute_time_ms"],
                                 navdata_std["mean_compute_time_ms"] + 1*navdata_std["std_compute_time_ms"],
                                 alpha=0.5)
        plt.yscale("log")
        save_figure(fig,graph_type+"_"+"mean_compute_time_ms")

def accuracy_plots(simulated_results_path):
    """Create accuracy plots.

    Parameters
    ----------
    simulated_results_path : string
        Paths to saved metrics.

    """

    navdata = glp.NavData(csv_path = simulated_results_path)
    edm_navdata = navdata.where("method","edm")
    r_navdata = navdata.where("method","residual")

    glp.plot_metric(edm_navdata,
                    "threshold","balanced_accuracy",
                    groupby="bias",
                    save=True,
                    prefix="edm_bias",
                    avg_y=True,
                    linewidth=5.0,
                    markersize=10,
                    )
    plt.ylim(0.4,1.0)

    glp.plot_metric(edm_navdata.where("bias",60),
                    "threshold","balanced_accuracy",
                    groupby="faults",
                    save=True,
                    prefix="edm_faults",
                    avg_y=True,
                    linewidth=5.0,
                    markersize=10,
                    )
    plt.ylim(0.4,1.0)

    glp.plot_metric(r_navdata,
                    "threshold","balanced_accuracy",
                    groupby="bias",
                    save=True,
                    prefix="residual_bias",
                    avg_y=True,
                    linewidth=5.0,
                    markersize=10
                    )
    plt.ylim(0.4,1.0)

    edm_navdata["method_and_bias_m"] = np.array(["edm_"+str(b)+"_m" for b in edm_navdata["bias"]])
    fig = glp.plot_metric(edm_navdata.where("threshold",0.5700000000000001),
                    "faults","balanced_accuracy",
                    groupby="method_and_bias_m",
                    save=True,
                    avg_y=True,
                    linewidth=5.0,
                    markersize=10
                    )
    plt.ylim(0.4,1.0)

    r_navdata["method_and_bias_m"] = np.array(["residual_"+str(b)+"_m" for b in r_navdata["bias"]])
    glp.plot_metric(r_navdata.where("threshold",17.),
                    "faults","balanced_accuracy",
                    groupby="method_and_bias_m",
                    save=True,
                    prefix="faults_vs_ba",
                    avg_y=True,
                    linewidth=5.0,
                    markersize=10,
                    linestyle="dotted",
                    fig=fig,
                    )
    plt.ylim(0.4,1.0)


def simulated_data_metrics():
    """Calculate metrics based on the simulated data.

    """
    metrics = glp.NavData()

    for location_name, i in locations.items():
        csv_path = os.path.join(os.getcwd(),"data",
                                "simulated",location_name + "_20230314.csv")

        navdata = glp.NavData(csv_path=csv_path)

        metrics_subset = glp.NavData()

        sats_in_view = []
        gps_millis = []
        for timestamp,_,subset in glp.loop_time(navdata,"gps_millis"):
            sats_in_view.append(len(np.unique(subset["gnss_sv_id"])))
            gps_millis.append(timestamp)

        metrics_subset["sats_in_view"] = sats_in_view
        metrics_subset["gps_millis"] = gps_millis
        metrics_subset["location_name"] = np.array([location_name]*len(sats_in_view))
        metrics = glp.concat(metrics,metrics_subset)

    print("total_timesteps:",len(np.unique(metrics["gps_millis"])),len(metrics))
    print("min sats in view:",np.min(metrics["sats_in_view"]))
    print("mean sats in view:",np.mean(metrics["sats_in_view"]))
    print("max sats in view:",np.max(metrics["sats_in_view"]))

def plot_sats_in_view():
    """Calculate the satellites in view and plot.

    """
    metrics = glp.NavData()

    for location_name, i in locations.items():
        csv_path = os.path.join(os.getcwd(),"data",
                                "simulated",location_name + "_20230314.csv")

        navdata = glp.NavData(csv_path=csv_path)
        if location_name in ("calgary","zurich","london"):
            navdata = navdata.where("el_sv_deg",30.,"geq")

        metrics_subset = glp.NavData()

        sats_in_view = []
        gps_millis = []
        for timestamp,_,subset in glp.loop_time(navdata,"gps_millis"):
            sats_in_view.append(len(np.unique(subset["gnss_sv_id"])))
            gps_millis.append(timestamp)

        metrics_subset["sats_in_view"] = sats_in_view
        metrics_subset["gps_millis"] = gps_millis
        metrics_subset["location_name"] = np.array([location_name]*len(sats_in_view))
        metrics = glp.concat(metrics,metrics_subset)

    metrics["time_hr"] = (metrics["gps_millis"] - metrics["gps_millis",0])/(1000*60*60.)

    fig = glp.plot_metric(metrics,"time_hr","sats_in_view",
                          groupby="location_name")
    plt.xlim([0,24])
    save_figure(fig,"sats_in_view")

def world_skyplots():
    """Plot the chosen world skkyplots.

    """
    for location_name, i in locations.items():
        # only plot those used for presentation
        if location_name in ("sao_paulo","hong_kong","zurich"):
            csv_path = os.path.join(os.getcwd(),"data",
                                    "simulated",location_name + "_20230314.csv")

            navdata = glp.NavData(csv_path=csv_path)

            timestamp_start = datetime(year=2023, month=3, day=14, hour=i, tzinfo=timezone.utc)
            timestamp_end = datetime(year=2023, month=3, day=14, hour=i+1, tzinfo=timezone.utc)
            gps_millis = glp.datetime_to_gps_millis(np.array([timestamp_start,timestamp_end]))
            cropped_navdata = navdata.where("gps_millis",gps_millis[0],"geq").where("gps_millis",gps_millis[1],"leq")
            glp.plot_skyplot(cropped_navdata,cropped_navdata,
                             prefix=location_name,save=True)

def world_skyplots_check():
    """Plot each of the location skyplots.

    """
    for location_name, _ in locations.items():
        print("location name:",location_name)
        csv_path = os.path.join(os.getcwd(),"data",
                                "simulated",location_name + "_20230314.csv")

        navdata = glp.NavData(csv_path=csv_path)

        for i in range(0,23):
            timestamp_start = datetime(year=2023, month=3, day=14, hour=i, tzinfo=timezone.utc)
            timestamp_end = datetime(year=2023, month=3, day=14, hour=i+1, tzinfo=timezone.utc)
            gps_millis = glp.datetime_to_gps_millis(np.array([timestamp_start,timestamp_end]))
            cropped_navdata = navdata.where("gps_millis",gps_millis[0],"geq").where("gps_millis",gps_millis[1],"leq")
            print(i,len(np.unique(cropped_navdata["gnss_id"])),
                    len(np.unique(cropped_navdata["gnss_sv_id"])))

def moving_svd(noise):
    """Plot the U matrix from singular value decomposition.

    Parameters
    ----------
    noise : bool
        If true, adds noise to the data.

    """
    file_path = os.path.join(os.getcwd(),"data","simulated",
                             "stanford_oval_20230314.csv")
    navdata = glp.NavData(csv_path=file_path)

    navdata = navdata.copy(cols=np.arange(1,10))

    if noise:
        navdata["corr_pr_m"] += np.random.normal(loc=0.0,scale=10,size=len(navdata))

    navdata["corr_pr_m",3] += 1000.
    edm = _edm_from_satellites_ranges(navdata[["x_sv_m","y_sv_m","z_sv_m"]],
                                      navdata["corr_pr_m"])

    dims = edm.shape[1]
    center = np.eye(dims) - (1./dims) * np.ones((dims,dims))
    gram = -0.5 * center @ edm @ center

    # calculate the singular value decomposition
    svd_u, _, _ = np.linalg.svd(gram,full_matrices=True)

    fig = plt.figure(figsize=(3.5,3.5))
    plt.imshow(np.abs(svd_u),cmap="cividis")
    plt.colorbar()
    save_figure(fig,"u_1_faults")


def moving_eigenvalues(noise):
    """Plot the singular values from singular value decomposition.

    Parameters
    ----------
    noise : bool
        If true, adds noise to the data.

    """

    file_path = os.path.join(os.getcwd(),"data","simulated",
                             "stanford_oval_20230314.csv")
    navdata = glp.NavData(csv_path=file_path)
    navdata = navdata.copy(cols=list(np.arange(20)))

    if noise:
        navdata["corr_pr_m"] += np.random.normal(loc=0.0,scale=10,size=len(navdata))

    edm = _edm_from_satellites_ranges(navdata[["x_sv_m","y_sv_m","z_sv_m"]],
                                      navdata["corr_pr_m"])

    dims = edm.shape[1]
    center = np.eye(dims) - (1./dims) * np.ones((dims,dims))
    gram = -0.5 * center @ edm @ center

    # calculate the singular value decomposition
    _, svd_s, _ = np.linalg.svd(gram,full_matrices=True)

    data = glp.NavData()
    data["eigenvalue_magnitude"] = svd_s
    data["number_of_faults"] = np.array(["0 faults"]*len(data))

    plt.rcParams['figure.figsize'] = [5.9, 3.5]
    fig = glp.plot_metric(data,"eigenvalue_magnitude",
                          groupby="number_of_faults",
                          linestyle="None", title="", markersize=8,)
    plt.xlim([-0.5,len(data)-0.5])
    plt.yscale("log")
    plt.ylim(1E-5,1E17)
    if noise:
        save_figure(fig,"faults_with_noise_"+str(0).zfill(2))
        save_figure(fig,"faults_with_noise_"+str(19).zfill(2))
    else:
        save_figure(fig,"faults_"+str(0).zfill(2))
        save_figure(fig,"faults_"+str(19).zfill(2))


    for i in range(1,10):

        navdata["corr_pr_m",i] += 1000.
        edm = _edm_from_satellites_ranges(navdata[["x_sv_m","y_sv_m","z_sv_m"]],
                                          navdata["corr_pr_m"])

        dims = edm.shape[1]
        center = np.eye(dims) - (1./dims) * np.ones((dims,dims))
        gram = -0.5 * center @ edm @ center

        # calculate the singular value decomposition
        svd_u, svd_s, svd_vt = np.linalg.svd(gram,full_matrices=True)

        data_fault = glp.NavData()
        data_fault["eigenvalue_magnitude"] = svd_s
        if i == 1:
            data_fault["number_of_faults"] = np.array([str(i) + " fault"]*len(data_fault))
        else:
            data_fault["number_of_faults"] = np.array([str(i) + " faults"]*len(data_fault))

        data = glp.concat(data,data_fault)
        plt.rcParams['figure.figsize'] = [5.9, 3.5]
        fig = glp.plot_metric(data,"eigenvalue_magnitude",
                              groupby="number_of_faults",
                              linestyle="None", title="", markersize=8,)
        plt.xlim([-0.5,len(data_fault)-0.5])
        plt.yscale("log")
        plt.ylim(1E-5,1E17)
        if noise:
            save_figure(fig,"faults_with_noise_"+str(i).zfill(2))
            save_figure(fig,"faults_with_noise_"+str(19-i).zfill(2))
        else:
            save_figure(fig,"faults_"+str(i).zfill(2))
            save_figure(fig,"faults_"+str(19-i).zfill(2))

        plt.close(fig)

if __name__ == "__main__":
    main()
