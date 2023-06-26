\ Model CentralizedModel_Gurobi
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0.04 flow[S6,A3,Transmission] + 0.045 flow[S5,A2,Transmission]
   + 0.06 flow[S7,A3,Transmission] + 0.06 flow[S6,A1,Transmission]
   + 0.05 flow[S7,A1,Transmission]
   + 0.0450888350748882 flow[S6,A2,Transmission]
   + 0.05 flow[S5,A3,Transmission]
   + 0.0420290706073302 flow[S7,A2,Transmission]
   + 0.045 flow[S5,A1,Transmission]
   + 3.048843702834902 flow[S3,A3,Dashboard]
   + 3.285716879737123 flow[S4,A1,Dashboard]
   + 2.831994621215886 flow[S3,A1,Dashboard]
   + 3.081580185407506 flow[S4,A2,Dashboard]
   + 2.982712699227799 flow[S3,A2,Dashboard]
   + 3.573666906478998 flow[S4,A3,Dashboard]
   + 2.741293826288751 flow[S2,A2,PowerTrain2]
   + 2.719310805387702 flow[S2,A3,PowerTrain2]
   + 2.485003771776892 flow[S2,A1,PowerTrain2]
   + 0.2052039994894401 flow[S1,A3,PowerTrain1]
   + 0.2172485568390397 flow[S1,A1,PowerTrain1]
   + 0.18410095683703 flow[S1,A2,PowerTrain1]
   + 1.055662460379671 flow[A1,D1,Vehicle1]
   + 1.046001298116628 flow[A1,D2,Vehicle1]
   + 1.498726522753701 flow[A3,D2,Vehicle2]
   + 1.140581363864388 flow[A2,D1,Vehicle2]
   + 1.246195460940014 flow[A2,D2,Vehicle2]
   + 1.28476926710635 flow[A3,D1,Vehicle2]
   + 1.243739389173541 flow[D1,C2,Vehicle1]
   + 1.326854704902049 flow[D2,C1,Vehicle1]
   + 1.243739389173541 flow[D1,C1,Vehicle1]
   + 1.326854704902049 flow[D2,C2,Vehicle1]
   + 1.243739389173541 flow[D1,C2,Vehicle2]
   + 1.326854704902049 flow[D2,C1,Vehicle2]
   + 1.243739389173541 flow[D1,C1,Vehicle2]
   + 1.326854704902049 flow[D2,C2,Vehicle2]
   + 0.01 link_product_usage[S6,A3,Transmission]
   + 0.01 link_product_usage[S5,A2,Transmission]
   + 0.01 link_product_usage[S7,A3,Transmission]
   + 0.01 link_product_usage[S6,A1,Transmission]
   + 0.01 link_product_usage[S7,A1,Transmission]
   + 0.01 link_product_usage[S6,A2,Transmission]
   + 0.01 link_product_usage[S5,A3,Transmission]
   + 0.01 link_product_usage[S7,A2,Transmission]
   + 0.01 link_product_usage[S5,A1,Transmission]
   + 0.01 link_product_usage[S3,A3,Dashboard]
   + 0.01 link_product_usage[S4,A1,Dashboard]
   + 0.01 link_product_usage[S3,A1,Dashboard]
   + 0.01 link_product_usage[S4,A2,Dashboard]
   + 0.01 link_product_usage[S3,A2,Dashboard]
   + 0.01 link_product_usage[S4,A3,Dashboard]
   + 0.01 link_product_usage[S2,A2,PowerTrain2]
   + 0.01 link_product_usage[S2,A3,PowerTrain2]
   + 0.01 link_product_usage[S2,A1,PowerTrain2]
   + 0.01 link_product_usage[S1,A3,PowerTrain1]
   + 0.01 link_product_usage[S1,A1,PowerTrain1]
   + 0.01 link_product_usage[S1,A2,PowerTrain1]
   + 0.01 link_product_usage[A1,D1,Vehicle1]
   + 0.01 link_product_usage[A1,D2,Vehicle1]
   + 0.01 link_product_usage[A3,D2,Vehicle2]
   + 0.01 link_product_usage[A2,D1,Vehicle2]
   + 0.01 link_product_usage[A2,D2,Vehicle2]
   + 0.01 link_product_usage[A3,D1,Vehicle2]
   + 0.01 link_product_usage[D1,C2,Vehicle1]
   + 0.01 link_product_usage[D2,C1,Vehicle1]
   + 0.01 link_product_usage[D1,C1,Vehicle1]
   + 0.01 link_product_usage[D2,C2,Vehicle1]
   + 0.01 link_product_usage[D1,C2,Vehicle2]
   + 0.01 link_product_usage[D2,C1,Vehicle2]
   + 0.01 link_product_usage[D1,C1,Vehicle2]
   + 0.01 link_product_usage[D2,C2,Vehicle2] + 0.01 prodLine_usage[S4]
   + 0.01 prodLine_usage[S6] + 0.01 prodLine_usage[C1]
   + 0.01 prodLine_usage[S1] + 0.01 prodLine_usage[A3]
   + 0.01 prodLine_usage[A1] + 0.01 prodLine_usage[S2]
   + 0.01 prodLine_usage[S3] + 0.01 prodLine_usage[D2]
   + 0.01 prodLine_usage[S5] + 0.01 prodLine_usage[A2]
   + 0.01 prodLine_usage[S7] + 0.01 prodLine_usage[D1]
   + 0.01 prodLine_usage[C2] + 0 duedate_exceeded[S6,A3,Transmission]
   + 0 duedate_exceeded[S5,A2,Transmission]
   + 0 duedate_exceeded[S7,A3,Transmission]
   + 0 duedate_exceeded[S6,A1,Transmission]
   + 0 duedate_exceeded[S7,A1,Transmission]
   + 0 duedate_exceeded[S6,A2,Transmission]
   + 0 duedate_exceeded[S5,A3,Transmission]
   + 0 duedate_exceeded[S7,A2,Transmission]
   + 0 duedate_exceeded[S5,A1,Transmission]
   + 0 duedate_exceeded[S3,A3,Dashboard]
   + 0 duedate_exceeded[S4,A1,Dashboard]
   + 0 duedate_exceeded[S3,A1,Dashboard]
   + 0 duedate_exceeded[S4,A2,Dashboard]
   + 0 duedate_exceeded[S3,A2,Dashboard]
   + 0 duedate_exceeded[S4,A3,Dashboard]
   + 0 duedate_exceeded[S2,A2,PowerTrain2]
   + 0 duedate_exceeded[S2,A3,PowerTrain2]
   + 0 duedate_exceeded[S2,A1,PowerTrain2]
   + 0 duedate_exceeded[S1,A3,PowerTrain1]
   + 0 duedate_exceeded[S1,A1,PowerTrain1]
   + 0 duedate_exceeded[S1,A2,PowerTrain1]
   + 0 duedate_exceeded[A1,D1,Vehicle1]
   + 0 duedate_exceeded[A1,D2,Vehicle1]
   + 0 duedate_exceeded[A3,D2,Vehicle2]
   + 0 duedate_exceeded[A2,D1,Vehicle2]
   + 0 duedate_exceeded[A2,D2,Vehicle2]
   + 0 duedate_exceeded[A3,D1,Vehicle2]
   + 0 duedate_exceeded[D1,C2,Vehicle1]
   + 0 duedate_exceeded[D2,C1,Vehicle1]
   + 0 duedate_exceeded[D1,C1,Vehicle1]
   + 0 duedate_exceeded[D2,C2,Vehicle1]
   + 0 duedate_exceeded[D1,C2,Vehicle2]
   + 0 duedate_exceeded[D2,C1,Vehicle2]
   + 0 duedate_exceeded[D1,C1,Vehicle2]
   + 0 duedate_exceeded[D2,C2,Vehicle2] + 14.01 run_length[S4,Dashboard]
   + 0.88 run_length[S6,Transmission] + 1.03 run_length[S1,PowerTrain1]
   + 2.2 run_length[A3,Vehicle2] + 2.65 run_length[A1,Vehicle1]
   + 1.07 run_length[S2,PowerTrain2] + 14.52 run_length[S3,Dashboard]
   + 0.83 run_length[S5,Transmission] + 2.39 run_length[A2,Vehicle2]
   + 0.85 run_length[S7,Transmission] + inventory[S4,Dashboard]
   + inventory[S6,Transmission] + inventory[C1,Vehicle1]
   + inventory[S1,PowerTrain1] + inventory[A3,PowerTrain2]
   + inventory[A3,Transmission] + inventory[A3,Dashboard]
   + inventory[A3,Vehicle2] + inventory[A1,PowerTrain1]
   + inventory[A1,Transmission] + inventory[A1,Dashboard]
   + inventory[A1,Vehicle1] + inventory[S2,PowerTrain2]
   + inventory[S3,Dashboard] + inventory[D2,Vehicle1]
   + inventory[D2,Vehicle2] + inventory[S5,Transmission]
   + inventory[A2,PowerTrain2] + inventory[A2,Transmission]
   + inventory[A2,Dashboard] + inventory[A2,Vehicle2]
   + inventory[S7,Transmission] + inventory[D1,Vehicle1]
   + inventory[D1,Vehicle2] + inventory[C2,Vehicle2]
   + 100 penalty_demand[S4,Dashboard] + 100 penalty_demand[S6,Transmission]
   + 100 penalty_demand[C1,Vehicle1] + 100 penalty_demand[S1,PowerTrain1]
   + 100 penalty_demand[A3,PowerTrain2]
   + 100 penalty_demand[A3,Transmission] + 100 penalty_demand[A3,Dashboard]
   + 100 penalty_demand[A3,Vehicle2] + 100 penalty_demand[A1,PowerTrain1]
   + 100 penalty_demand[A1,Transmission] + 100 penalty_demand[A1,Dashboard]
   + 100 penalty_demand[A1,Vehicle1] + 100 penalty_demand[S2,PowerTrain2]
   + 100 penalty_demand[S3,Dashboard] + 100 penalty_demand[D2,Vehicle1]
   + 100 penalty_demand[D2,Vehicle2] + 100 penalty_demand[S5,Transmission]
   + 100 penalty_demand[A2,PowerTrain2]
   + 100 penalty_demand[A2,Transmission] + 100 penalty_demand[A2,Dashboard]
   + 100 penalty_demand[A2,Vehicle2] + 100 penalty_demand[S7,Transmission]
   + 100 penalty_demand[D1,Vehicle1] + 100 penalty_demand[D1,Vehicle2]
   + 100 penalty_demand[C2,Vehicle2] + penalty_inv[S4,Dashboard]
   + penalty_inv[S6,Transmission] + penalty_inv[C1,Vehicle1]
   + penalty_inv[S1,PowerTrain1] + penalty_inv[A3,PowerTrain2]
   + penalty_inv[A3,Transmission] + penalty_inv[A3,Dashboard]
   + penalty_inv[A3,Vehicle2] + penalty_inv[A1,PowerTrain1]
   + penalty_inv[A1,Transmission] + penalty_inv[A1,Dashboard]
   + penalty_inv[A1,Vehicle1] + penalty_inv[S2,PowerTrain2]
   + penalty_inv[S3,Dashboard] + penalty_inv[D2,Vehicle1]
   + penalty_inv[D2,Vehicle2] + penalty_inv[S5,Transmission]
   + penalty_inv[A2,PowerTrain2] + penalty_inv[A2,Transmission]
   + penalty_inv[A2,Dashboard] + penalty_inv[A2,Vehicle2]
   + penalty_inv[S7,Transmission] + penalty_inv[D1,Vehicle1]
   + penalty_inv[D1,Vehicle2] + penalty_inv[C2,Vehicle2]
   + 0 arrival_time[S6,A3,Transmission]
   + 0 arrival_time[S5,A2,Transmission]
   + 0 arrival_time[S7,A3,Transmission]
   + 0 arrival_time[S6,A1,Transmission]
   + 0 arrival_time[S7,A1,Transmission]
   + 0 arrival_time[S6,A2,Transmission]
   + 0 arrival_time[S5,A3,Transmission]
   + 0 arrival_time[S7,A2,Transmission]
   + 0 arrival_time[S5,A1,Transmission] + 0 arrival_time[S3,A3,Dashboard]
   + 0 arrival_time[S4,A1,Dashboard] + 0 arrival_time[S3,A1,Dashboard]
   + 0 arrival_time[S4,A2,Dashboard] + 0 arrival_time[S3,A2,Dashboard]
   + 0 arrival_time[S4,A3,Dashboard] + 0 arrival_time[S2,A2,PowerTrain2]
   + 0 arrival_time[S2,A3,PowerTrain2] + 0 arrival_time[S2,A1,PowerTrain2]
   + 0 arrival_time[S1,A3,PowerTrain1] + 0 arrival_time[S1,A1,PowerTrain1]
   + 0 arrival_time[S1,A2,PowerTrain1] + 0 arrival_time[A1,D1,Vehicle1]
   + 0 arrival_time[A1,D2,Vehicle1] + 0 arrival_time[A3,D2,Vehicle2]
   + 0 arrival_time[A2,D1,Vehicle2] + 0 arrival_time[A2,D2,Vehicle2]
   + 0 arrival_time[A3,D1,Vehicle2] + 0 arrival_time[D1,C2,Vehicle1]
   + 0 arrival_time[D2,C1,Vehicle1] + 0 arrival_time[D1,C1,Vehicle1]
   + 0 arrival_time[D2,C2,Vehicle1] + 0 arrival_time[D1,C2,Vehicle2]
   + 0 arrival_time[D2,C1,Vehicle2] + 0 arrival_time[D1,C1,Vehicle2]
   + 0 arrival_time[D2,C2,Vehicle2] + 0 initial_proc_time[S4,Dashboard]
   + 0 initial_proc_time[S6,Transmission]
   + 0 initial_proc_time[C1,Vehicle1] + 0 initial_proc_time[S1,PowerTrain1]
   + 0 initial_proc_time[A3,PowerTrain2]
   + 0 initial_proc_time[A3,Transmission]
   + 0 initial_proc_time[A3,Dashboard] + 0 initial_proc_time[A3,Vehicle2]
   + 0 initial_proc_time[A1,PowerTrain1]
   + 0 initial_proc_time[A1,Transmission]
   + 0 initial_proc_time[A1,Dashboard] + 0 initial_proc_time[A1,Vehicle1]
   + 0 initial_proc_time[S2,PowerTrain2]
   + 0 initial_proc_time[S3,Dashboard] + 0 initial_proc_time[D2,Vehicle1]
   + 0 initial_proc_time[D2,Vehicle2]
   + 0 initial_proc_time[S5,Transmission]
   + 0 initial_proc_time[A2,PowerTrain2]
   + 0 initial_proc_time[A2,Transmission]
   + 0 initial_proc_time[A2,Dashboard] + 0 initial_proc_time[A2,Vehicle2]
   + 0 initial_proc_time[S7,Transmission]
   + 0 initial_proc_time[D1,Vehicle1] + 0 initial_proc_time[D1,Vehicle2]
   + 0 initial_proc_time[C2,Vehicle2] + 0 product_z_a[S6,A3,Transmission]
   + 0 product_z_a[S5,A2,Transmission] + 0 product_z_a[S7,A3,Transmission]
   + 0 product_z_a[S6,A1,Transmission] + 0 product_z_a[S7,A1,Transmission]
   + 0 product_z_a[S6,A2,Transmission] + 0 product_z_a[S5,A3,Transmission]
   + 0 product_z_a[S7,A2,Transmission] + 0 product_z_a[S5,A1,Transmission]
   + 0 product_z_a[S3,A3,Dashboard] + 0 product_z_a[S4,A1,Dashboard]
   + 0 product_z_a[S3,A1,Dashboard] + 0 product_z_a[S4,A2,Dashboard]
   + 0 product_z_a[S3,A2,Dashboard] + 0 product_z_a[S4,A3,Dashboard]
   + 0 product_z_a[S2,A2,PowerTrain2] + 0 product_z_a[S2,A3,PowerTrain2]
   + 0 product_z_a[S2,A1,PowerTrain2] + 0 product_z_a[S1,A3,PowerTrain1]
   + 0 product_z_a[S1,A1,PowerTrain1] + 0 product_z_a[S1,A2,PowerTrain1]
   + 0 product_z_a[A1,D1,Vehicle1] + 0 product_z_a[A1,D2,Vehicle1]
   + 0 product_z_a[A3,D2,Vehicle2] + 0 product_z_a[A2,D1,Vehicle2]
   + 0 product_z_a[A2,D2,Vehicle2] + 0 product_z_a[A3,D1,Vehicle2]
   + 0 product_z_a[D1,C2,Vehicle1] + 0 product_z_a[D2,C1,Vehicle1]
   + 0 product_z_a[D1,C1,Vehicle1] + 0 product_z_a[D2,C2,Vehicle1]
   + 0 product_z_a[D1,C2,Vehicle2] + 0 product_z_a[D2,C1,Vehicle2]
   + 0 product_z_a[D1,C1,Vehicle2] + 0 product_z_a[D2,C2,Vehicle2]
   + 0 product_beta_o[S6,A3,Transmission]
   + 0 product_beta_o[S5,A2,Transmission]
   + 0 product_beta_o[S7,A3,Transmission]
   + 0 product_beta_o[S6,A1,Transmission]
   + 0 product_beta_o[S7,A1,Transmission]
   + 0 product_beta_o[S6,A2,Transmission]
   + 0 product_beta_o[S5,A3,Transmission]
   + 0 product_beta_o[S7,A2,Transmission]
   + 0 product_beta_o[S5,A1,Transmission]
   + 0 product_beta_o[S3,A3,Dashboard] + 0 product_beta_o[S4,A1,Dashboard]
   + 0 product_beta_o[S3,A1,Dashboard] + 0 product_beta_o[S4,A2,Dashboard]
   + 0 product_beta_o[S3,A2,Dashboard] + 0 product_beta_o[S4,A3,Dashboard]
   + 0 product_beta_o[S2,A2,PowerTrain2]
   + 0 product_beta_o[S2,A3,PowerTrain2]
   + 0 product_beta_o[S2,A1,PowerTrain2]
   + 0 product_beta_o[S1,A3,PowerTrain1]
   + 0 product_beta_o[S1,A1,PowerTrain1]
   + 0 product_beta_o[S1,A2,PowerTrain1] + 0 product_beta_o[A1,D1,Vehicle1]
   + 0 product_beta_o[A1,D2,Vehicle1] + 0 product_beta_o[A3,D2,Vehicle2]
   + 0 product_beta_o[A2,D1,Vehicle2] + 0 product_beta_o[A2,D2,Vehicle2]
   + 0 product_beta_o[A3,D1,Vehicle2] + 0 product_beta_o[D1,C2,Vehicle1]
   + 0 product_beta_o[D2,C1,Vehicle1] + 0 product_beta_o[D1,C1,Vehicle1]
   + 0 product_beta_o[D2,C2,Vehicle1] + 0 product_beta_o[D1,C2,Vehicle2]
   + 0 product_beta_o[D2,C1,Vehicle2] + 0 product_beta_o[D1,C1,Vehicle2]
   + 0 product_beta_o[D2,C2,Vehicle2]
   + total_penalty_computed[S6,A3,Transmission]
   + total_penalty_computed[S5,A2,Transmission]
   + total_penalty_computed[S7,A3,Transmission]
   + total_penalty_computed[S6,A1,Transmission]
   + total_penalty_computed[S7,A1,Transmission]
   + total_penalty_computed[S6,A2,Transmission]
   + total_penalty_computed[S5,A3,Transmission]
   + total_penalty_computed[S7,A2,Transmission]
   + total_penalty_computed[S5,A1,Transmission]
   + total_penalty_computed[S3,A3,Dashboard]
   + total_penalty_computed[S4,A1,Dashboard]
   + total_penalty_computed[S3,A1,Dashboard]
   + total_penalty_computed[S4,A2,Dashboard]
   + total_penalty_computed[S3,A2,Dashboard]
   + total_penalty_computed[S4,A3,Dashboard]
   + total_penalty_computed[S2,A2,PowerTrain2]
   + total_penalty_computed[S2,A3,PowerTrain2]
   + total_penalty_computed[S2,A1,PowerTrain2]
   + total_penalty_computed[S1,A3,PowerTrain1]
   + total_penalty_computed[S1,A1,PowerTrain1]
   + total_penalty_computed[S1,A2,PowerTrain1]
   + total_penalty_computed[A1,D1,Vehicle1]
   + total_penalty_computed[A1,D2,Vehicle1]
   + total_penalty_computed[A3,D2,Vehicle2]
   + total_penalty_computed[A2,D1,Vehicle2]
   + total_penalty_computed[A2,D2,Vehicle2]
   + total_penalty_computed[A3,D1,Vehicle2]
   + total_penalty_computed[D1,C2,Vehicle1]
   + total_penalty_computed[D2,C1,Vehicle1]
   + total_penalty_computed[D1,C1,Vehicle1]
   + total_penalty_computed[D2,C2,Vehicle1]
   + total_penalty_computed[D1,C2,Vehicle2]
   + total_penalty_computed[D2,C1,Vehicle2]
   + total_penalty_computed[D1,C1,Vehicle2]
   + total_penalty_computed[D2,C2,Vehicle2]
Subject To
 Flow_balance_constraints[S4,Dashboard]: flow[S4,A1,Dashboard]
   + flow[S4,A2,Dashboard] + flow[S4,A3,Dashboard]
   - demand_satisfied[S4,Dashboard] - run_length[S4,Dashboard]
   + inventory[S4,Dashboard] = 0
 Flow_balance_constraints[S6,Transmission]: flow[S6,A3,Transmission]
   + flow[S6,A1,Transmission] + flow[S6,A2,Transmission]
   - demand_satisfied[S6,Transmission] - run_length[S6,Transmission]
   + inventory[S6,Transmission] = 0
 Flow_balance_constraints[C1,Vehicle1]: - flow[D2,C1,Vehicle1]
   - flow[D1,C1,Vehicle1] - demand_satisfied[C1,Vehicle1]
   - run_length[C1,Vehicle1] + inventory[C1,Vehicle1] = 0
 Flow_balance_constraints[S1,PowerTrain1]: flow[S1,A3,PowerTrain1]
   + flow[S1,A1,PowerTrain1] + flow[S1,A2,PowerTrain1]
   - demand_satisfied[S1,PowerTrain1] - run_length[S1,PowerTrain1]
   + inventory[S1,PowerTrain1] = 0
 Flow_balance_constraints[A3,PowerTrain2]: - flow[S2,A3,PowerTrain2]
   - demand_satisfied[A3,PowerTrain2] + run_length[A3,Vehicle2]
   + inventory[A3,PowerTrain2] = 0
 Flow_balance_constraints[A3,Transmission]: - flow[S6,A3,Transmission]
   - flow[S7,A3,Transmission] - flow[S5,A3,Transmission]
   - demand_satisfied[A3,Transmission] + run_length[A3,Vehicle2]
   + inventory[A3,Transmission] = 0
 Flow_balance_constraints[A3,Dashboard]: - flow[S3,A3,Dashboard]
   - flow[S4,A3,Dashboard] - demand_satisfied[A3,Dashboard]
   + run_length[A3,Vehicle2] + inventory[A3,Dashboard] = 0
 Flow_balance_constraints[A3,Vehicle2]: flow[A3,D2,Vehicle2]
   + flow[A3,D1,Vehicle2] - demand_satisfied[A3,Vehicle2]
   - run_length[A3,Vehicle2] + inventory[A3,Vehicle2] = 0
 Flow_balance_constraints[A1,PowerTrain1]: - flow[S1,A1,PowerTrain1]
   - demand_satisfied[A1,PowerTrain1] + run_length[A1,Vehicle1]
   + inventory[A1,PowerTrain1] = 0
 Flow_balance_constraints[A1,Transmission]: - flow[S6,A1,Transmission]
   - flow[S7,A1,Transmission] - flow[S5,A1,Transmission]
   - demand_satisfied[A1,Transmission] + run_length[A1,Vehicle1]
   + inventory[A1,Transmission] = 0
 Flow_balance_constraints[A1,Dashboard]: - flow[S4,A1,Dashboard]
   - flow[S3,A1,Dashboard] - demand_satisfied[A1,Dashboard]
   + run_length[A1,Vehicle1] + inventory[A1,Dashboard] = 0
 Flow_balance_constraints[A1,Vehicle1]: flow[A1,D1,Vehicle1]
   + flow[A1,D2,Vehicle1] - demand_satisfied[A1,Vehicle1]
   - run_length[A1,Vehicle1] + inventory[A1,Vehicle1] = 0
 Flow_balance_constraints[S2,PowerTrain2]: flow[S2,A2,PowerTrain2]
   + flow[S2,A3,PowerTrain2] + flow[S2,A1,PowerTrain2]
   - demand_satisfied[S2,PowerTrain2] - run_length[S2,PowerTrain2]
   + inventory[S2,PowerTrain2] = 0
 Flow_balance_constraints[S3,Dashboard]: flow[S3,A3,Dashboard]
   + flow[S3,A1,Dashboard] + flow[S3,A2,Dashboard]
   - demand_satisfied[S3,Dashboard] - run_length[S3,Dashboard]
   + inventory[S3,Dashboard] = 0
 Flow_balance_constraints[D2,Vehicle1]: - flow[A1,D2,Vehicle1]
   + flow[D2,C1,Vehicle1] + flow[D2,C2,Vehicle1]
   - demand_satisfied[D2,Vehicle1] - run_length[D2,Vehicle1]
   + inventory[D2,Vehicle1] = 0
 Flow_balance_constraints[D2,Vehicle2]: - flow[A3,D2,Vehicle2]
   - flow[A2,D2,Vehicle2] + flow[D2,C1,Vehicle2] + flow[D2,C2,Vehicle2]
   - demand_satisfied[D2,Vehicle2] - run_length[D2,Vehicle2]
   + inventory[D2,Vehicle2] = 0
 Flow_balance_constraints[S5,Transmission]: flow[S5,A2,Transmission]
   + flow[S5,A3,Transmission] + flow[S5,A1,Transmission]
   - demand_satisfied[S5,Transmission] - run_length[S5,Transmission]
   + inventory[S5,Transmission] = 0
 Flow_balance_constraints[A2,PowerTrain2]: - flow[S2,A2,PowerTrain2]
   - demand_satisfied[A2,PowerTrain2] + run_length[A2,Vehicle2]
   + inventory[A2,PowerTrain2] = 0
 Flow_balance_constraints[A2,Transmission]: - flow[S5,A2,Transmission]
   - flow[S6,A2,Transmission] - flow[S7,A2,Transmission]
   - demand_satisfied[A2,Transmission] + run_length[A2,Vehicle2]
   + inventory[A2,Transmission] = 0
 Flow_balance_constraints[A2,Dashboard]: - flow[S4,A2,Dashboard]
   - flow[S3,A2,Dashboard] - demand_satisfied[A2,Dashboard]
   + run_length[A2,Vehicle2] + inventory[A2,Dashboard] = 0
 Flow_balance_constraints[A2,Vehicle2]: flow[A2,D1,Vehicle2]
   + flow[A2,D2,Vehicle2] - demand_satisfied[A2,Vehicle2]
   - run_length[A2,Vehicle2] + inventory[A2,Vehicle2] = 0
 Flow_balance_constraints[S7,Transmission]: flow[S7,A3,Transmission]
   + flow[S7,A1,Transmission] + flow[S7,A2,Transmission]
   - demand_satisfied[S7,Transmission] - run_length[S7,Transmission]
   + inventory[S7,Transmission] = 0
 Flow_balance_constraints[D1,Vehicle1]: - flow[A1,D1,Vehicle1]
   + flow[D1,C2,Vehicle1] + flow[D1,C1,Vehicle1]
   - demand_satisfied[D1,Vehicle1] - run_length[D1,Vehicle1]
   + inventory[D1,Vehicle1] = 0
 Flow_balance_constraints[D1,Vehicle2]: - flow[A2,D1,Vehicle2]
   - flow[A3,D1,Vehicle2] + flow[D1,C2,Vehicle2] + flow[D1,C1,Vehicle2]
   - demand_satisfied[D1,Vehicle2] - run_length[D1,Vehicle2]
   + inventory[D1,Vehicle2] = 0
 Flow_balance_constraints[C2,Vehicle2]: - flow[D1,C2,Vehicle2]
   - flow[D2,C2,Vehicle2] - demand_satisfied[C2,Vehicle2]
   - run_length[C2,Vehicle2] + inventory[C2,Vehicle2] = 0
 Link_product_capacity[S6,A3,Transmission]: flow[S6,A3,Transmission]
   - 900 link_product_usage[S6,A3,Transmission] <= 0
 Link_product_capacity[S5,A2,Transmission]: flow[S5,A2,Transmission]
   - 10000 link_product_usage[S5,A2,Transmission] <= 0
 Link_product_capacity[S7,A3,Transmission]: flow[S7,A3,Transmission]
   - 10000 link_product_usage[S7,A3,Transmission] <= 0
 Link_product_capacity[S6,A1,Transmission]: flow[S6,A1,Transmission]
   - 3600 link_product_usage[S6,A1,Transmission] <= 0
 Link_product_capacity[S7,A1,Transmission]: flow[S7,A1,Transmission]
   - 10000 link_product_usage[S7,A1,Transmission] <= 0
 Link_product_capacity[S6,A2,Transmission]: flow[S6,A2,Transmission]
   - 2800 link_product_usage[S6,A2,Transmission] <= 0
 Link_product_capacity[S5,A3,Transmission]: flow[S5,A3,Transmission]
   - 10000 link_product_usage[S5,A3,Transmission] <= 0
 Link_product_capacity[S7,A2,Transmission]: flow[S7,A2,Transmission]
   - 10000 link_product_usage[S7,A2,Transmission] <= 0
 Link_product_capacity[S5,A1,Transmission]: flow[S5,A1,Transmission]
   - 10000 link_product_usage[S5,A1,Transmission] <= 0
 Link_product_capacity[S3,A3,Dashboard]: flow[S3,A3,Dashboard]
   - 10000 link_product_usage[S3,A3,Dashboard] <= 0
 Link_product_capacity[S4,A1,Dashboard]: flow[S4,A1,Dashboard]
   - 3900 link_product_usage[S4,A1,Dashboard] <= 0
 Link_product_capacity[S3,A1,Dashboard]: flow[S3,A1,Dashboard]
   - 10000 link_product_usage[S3,A1,Dashboard] <= 0
 Link_product_capacity[S4,A2,Dashboard]: flow[S4,A2,Dashboard]
   - 10000 link_product_usage[S4,A2,Dashboard] <= 0
 Link_product_capacity[S3,A2,Dashboard]: flow[S3,A2,Dashboard]
   - 4000 link_product_usage[S3,A2,Dashboard] <= 0
 Link_product_capacity[S4,A3,Dashboard]: flow[S4,A3,Dashboard]
   - 3500 link_product_usage[S4,A3,Dashboard] <= 0
 Link_product_capacity[S2,A2,PowerTrain2]: flow[S2,A2,PowerTrain2]
   - 10000 link_product_usage[S2,A2,PowerTrain2] <= 0
 Link_product_capacity[S2,A3,PowerTrain2]: flow[S2,A3,PowerTrain2]
   - 10000 link_product_usage[S2,A3,PowerTrain2] <= 0
 Link_product_capacity[S2,A1,PowerTrain2]: flow[S2,A1,PowerTrain2]
   - 10000 link_product_usage[S2,A1,PowerTrain2] <= 0
 Link_product_capacity[S1,A3,PowerTrain1]: flow[S1,A3,PowerTrain1]
   - 10000 link_product_usage[S1,A3,PowerTrain1] <= 0
 Link_product_capacity[S1,A1,PowerTrain1]: flow[S1,A1,PowerTrain1]
   - 10000 link_product_usage[S1,A1,PowerTrain1] <= 0
 Link_product_capacity[S1,A2,PowerTrain1]: flow[S1,A2,PowerTrain1]
   - 10000 link_product_usage[S1,A2,PowerTrain1] <= 0
 Link_product_capacity[A1,D1,Vehicle1]: flow[A1,D1,Vehicle1]
   - 300 link_product_usage[A1,D1,Vehicle1] <= 0
 Link_product_capacity[A1,D2,Vehicle1]: flow[A1,D2,Vehicle1]
   - 2000 link_product_usage[A1,D2,Vehicle1] <= 0
 Link_product_capacity[A3,D2,Vehicle2]: flow[A3,D2,Vehicle2]
   - 10000 link_product_usage[A3,D2,Vehicle2] <= 0
 Link_product_capacity[A2,D1,Vehicle2]: flow[A2,D1,Vehicle2]
   - 500 link_product_usage[A2,D1,Vehicle2] <= 0
 Link_product_capacity[A2,D2,Vehicle2]: flow[A2,D2,Vehicle2]
   - 2000 link_product_usage[A2,D2,Vehicle2] <= 0
 Link_product_capacity[A3,D1,Vehicle2]: flow[A3,D1,Vehicle2]
   - 10000 link_product_usage[A3,D1,Vehicle2] <= 0
 Link_product_capacity[D1,C2,Vehicle1]: flow[D1,C2,Vehicle1]
   - 10000 link_product_usage[D1,C2,Vehicle1] <= 0
 Link_product_capacity[D2,C1,Vehicle1]: flow[D2,C1,Vehicle1]
   - 10000 link_product_usage[D2,C1,Vehicle1] <= 0
 Link_product_capacity[D1,C1,Vehicle1]: flow[D1,C1,Vehicle1]
   - 10000 link_product_usage[D1,C1,Vehicle1] <= 0
 Link_product_capacity[D2,C2,Vehicle1]: flow[D2,C2,Vehicle1]
   - 10000 link_product_usage[D2,C2,Vehicle1] <= 0
 Link_product_capacity[D1,C2,Vehicle2]: flow[D1,C2,Vehicle2]
   - 10000 link_product_usage[D1,C2,Vehicle2] <= 0
 Link_product_capacity[D2,C1,Vehicle2]: flow[D2,C1,Vehicle2]
   - 10000 link_product_usage[D2,C1,Vehicle2] <= 0
 Link_product_capacity[D1,C1,Vehicle2]: flow[D1,C1,Vehicle2]
   - 10000 link_product_usage[D1,C1,Vehicle2] <= 0
 Link_product_capacity[D2,C2,Vehicle2]: flow[D2,C2,Vehicle2]
   - 10000 link_product_usage[D2,C2,Vehicle2] <= 0
 Link_capacity[S6,A3,Transmission]: flow[S6,A3,Transmission] <= 900
 Link_capacity[S5,A2,Transmission]: flow[S5,A2,Transmission] <= 10000
 Link_capacity[S7,A3,Transmission]: flow[S7,A3,Transmission] <= 10000
 Link_capacity[S6,A1,Transmission]: flow[S6,A1,Transmission] <= 3600
 Link_capacity[S7,A1,Transmission]: flow[S7,A1,Transmission] <= 10000
 Link_capacity[S6,A2,Transmission]: flow[S6,A2,Transmission] <= 2800
 Link_capacity[S5,A3,Transmission]: flow[S5,A3,Transmission] <= 10000
 Link_capacity[S7,A2,Transmission]: flow[S7,A2,Transmission] <= 10000
 Link_capacity[S5,A1,Transmission]: flow[S5,A1,Transmission] <= 10000
 Link_capacity[S3,A3,Dashboard]: flow[S3,A3,Dashboard] <= 10000
 Link_capacity[S4,A1,Dashboard]: flow[S4,A1,Dashboard] <= 3900
 Link_capacity[S3,A1,Dashboard]: flow[S3,A1,Dashboard] <= 10000
 Link_capacity[S4,A2,Dashboard]: flow[S4,A2,Dashboard] <= 10000
 Link_capacity[S3,A2,Dashboard]: flow[S3,A2,Dashboard] <= 4000
 Link_capacity[S4,A3,Dashboard]: flow[S4,A3,Dashboard] <= 3500
 Link_capacity[S2,A2,PowerTrain2]: flow[S2,A2,PowerTrain2] <= 10000
 Link_capacity[S2,A3,PowerTrain2]: flow[S2,A3,PowerTrain2] <= 10000
 Link_capacity[S2,A1,PowerTrain2]: flow[S2,A1,PowerTrain2] <= 10000
 Link_capacity[S1,A3,PowerTrain1]: flow[S1,A3,PowerTrain1] <= 10000
 Link_capacity[S1,A1,PowerTrain1]: flow[S1,A1,PowerTrain1] <= 10000
 Link_capacity[S1,A2,PowerTrain1]: flow[S1,A2,PowerTrain1] <= 10000
 Link_capacity[A1,D1,Vehicle1]: flow[A1,D1,Vehicle1] <= 300
 Link_capacity[A1,D2,Vehicle1]: flow[A1,D2,Vehicle1] <= 2000
 Link_capacity[A3,D2,Vehicle2]: flow[A3,D2,Vehicle2] <= 10000
 Link_capacity[A2,D1,Vehicle2]: flow[A2,D1,Vehicle2] <= 500
 Link_capacity[A2,D2,Vehicle2]: flow[A2,D2,Vehicle2] <= 2000
 Link_capacity[A3,D1,Vehicle2]: flow[A3,D1,Vehicle2] <= 10000
 Link_capacity[D1,C2,Vehicle1]: flow[D1,C2,Vehicle1] + flow[D1,C2,Vehicle2]
   <= 10000
 Link_capacity[D2,C1,Vehicle1]: flow[D2,C1,Vehicle1] + flow[D2,C1,Vehicle2]
   <= 10000
 Link_capacity[D1,C1,Vehicle1]: flow[D1,C1,Vehicle1] + flow[D1,C1,Vehicle2]
   <= 10000
 Link_capacity[D2,C2,Vehicle1]: flow[D2,C2,Vehicle1] + flow[D2,C2,Vehicle2]
   <= 10000
 Link_capacity[D1,C2,Vehicle2]: flow[D1,C2,Vehicle1] + flow[D1,C2,Vehicle2]
   <= 10000
 Link_capacity[D2,C1,Vehicle2]: flow[D2,C1,Vehicle1] + flow[D2,C1,Vehicle2]
   <= 10000
 Link_capacity[D1,C1,Vehicle2]: flow[D1,C1,Vehicle1] + flow[D1,C1,Vehicle2]
   <= 10000
 Link_capacity[D2,C2,Vehicle2]: flow[D2,C2,Vehicle1] + flow[D2,C2,Vehicle2]
   <= 10000
 production_capacity[S4,Dashboard]: - 6500 prodLine_usage[S4]
   + run_length[S4,Dashboard] <= 0
 production_capacity[S6,Transmission]: - 4000 prodLine_usage[S6]
   + run_length[S6,Transmission] <= 0
 production_capacity[C1,Vehicle1]: run_length[C1,Vehicle1] <= 0
 production_capacity[S1,PowerTrain1]: - 10000 prodLine_usage[S1]
   + run_length[S1,PowerTrain1] <= 0
 production_capacity[A3,PowerTrain2]: - 7000 prodLine_usage[A3]
   + run_length[A3,PowerTrain2] + run_length[A3,Transmission]
   + run_length[A3,Dashboard] + run_length[A3,Vehicle2] <= 0
 production_capacity[A3,Transmission]: - 7000 prodLine_usage[A3]
   + run_length[A3,PowerTrain2] + run_length[A3,Transmission]
   + run_length[A3,Dashboard] + run_length[A3,Vehicle2] <= 0
 production_capacity[A3,Dashboard]: - 7000 prodLine_usage[A3]
   + run_length[A3,PowerTrain2] + run_length[A3,Transmission]
   + run_length[A3,Dashboard] + run_length[A3,Vehicle2] <= 0
 production_capacity[A3,Vehicle2]: - 7000 prodLine_usage[A3]
   + run_length[A3,PowerTrain2] + run_length[A3,Transmission]
   + run_length[A3,Dashboard] + run_length[A3,Vehicle2] <= 0
 production_capacity[A1,PowerTrain1]: - 7000 prodLine_usage[A1]
   + run_length[A1,PowerTrain1] + run_length[A1,Transmission]
   + run_length[A1,Dashboard] + run_length[A1,Vehicle1] <= 0
 production_capacity[A1,Transmission]: - 7000 prodLine_usage[A1]
   + run_length[A1,PowerTrain1] + run_length[A1,Transmission]
   + run_length[A1,Dashboard] + run_length[A1,Vehicle1] <= 0
 production_capacity[A1,Dashboard]: - 7000 prodLine_usage[A1]
   + run_length[A1,PowerTrain1] + run_length[A1,Transmission]
   + run_length[A1,Dashboard] + run_length[A1,Vehicle1] <= 0
 production_capacity[A1,Vehicle1]: - 7000 prodLine_usage[A1]
   + run_length[A1,PowerTrain1] + run_length[A1,Transmission]
   + run_length[A1,Dashboard] + run_length[A1,Vehicle1] <= 0
 production_capacity[S2,PowerTrain2]: - 10000 prodLine_usage[S2]
   + run_length[S2,PowerTrain2] <= 0
 production_capacity[S3,Dashboard]: - 7500 prodLine_usage[S3]
   + run_length[S3,Dashboard] <= 0
 production_capacity[D2,Vehicle1]: run_length[D2,Vehicle1]
   + run_length[D2,Vehicle2] <= 0
 production_capacity[D2,Vehicle2]: run_length[D2,Vehicle1]
   + run_length[D2,Vehicle2] <= 0
 production_capacity[S5,Transmission]: - 3000 prodLine_usage[S5]
   + run_length[S5,Transmission] <= 0
 production_capacity[A2,PowerTrain2]: - 7000 prodLine_usage[A2]
   + run_length[A2,PowerTrain2] + run_length[A2,Transmission]
   + run_length[A2,Dashboard] + run_length[A2,Vehicle2] <= 0
 production_capacity[A2,Transmission]: - 7000 prodLine_usage[A2]
   + run_length[A2,PowerTrain2] + run_length[A2,Transmission]
   + run_length[A2,Dashboard] + run_length[A2,Vehicle2] <= 0
 production_capacity[A2,Dashboard]: - 7000 prodLine_usage[A2]
   + run_length[A2,PowerTrain2] + run_length[A2,Transmission]
   + run_length[A2,Dashboard] + run_length[A2,Vehicle2] <= 0
 production_capacity[A2,Vehicle2]: - 7000 prodLine_usage[A2]
   + run_length[A2,PowerTrain2] + run_length[A2,Transmission]
   + run_length[A2,Dashboard] + run_length[A2,Vehicle2] <= 0
 production_capacity[S7,Transmission]: - 2000 prodLine_usage[S7]
   + run_length[S7,Transmission] <= 0
 production_capacity[D1,Vehicle1]: run_length[D1,Vehicle1]
   + run_length[D1,Vehicle2] <= 0
 production_capacity[D1,Vehicle2]: run_length[D1,Vehicle1]
   + run_length[D1,Vehicle2] <= 0
 production_capacity[C2,Vehicle2]: run_length[C2,Vehicle2] <= 0
 Demand_penalty[S4,Dashboard]: - demand_satisfied[S4,Dashboard]
   + penalty_demand[S4,Dashboard] >= 0
 Demand_penalty[S6,Transmission]: - demand_satisfied[S6,Transmission]
   + penalty_demand[S6,Transmission] >= 0
 Demand_penalty[C1,Vehicle1]: - demand_satisfied[C1,Vehicle1]
   + penalty_demand[C1,Vehicle1] >= 2300
 Demand_penalty[S1,PowerTrain1]: - demand_satisfied[S1,PowerTrain1]
   + penalty_demand[S1,PowerTrain1] >= 0
 Demand_penalty[A3,PowerTrain2]: - demand_satisfied[A3,PowerTrain2]
   + penalty_demand[A3,PowerTrain2] >= 0
 Demand_penalty[A3,Transmission]: - demand_satisfied[A3,Transmission]
   + penalty_demand[A3,Transmission] >= 0
 Demand_penalty[A3,Dashboard]: - demand_satisfied[A3,Dashboard]
   + penalty_demand[A3,Dashboard] >= 0
 Demand_penalty[A3,Vehicle2]: - demand_satisfied[A3,Vehicle2]
   + penalty_demand[A3,Vehicle2] >= 0
 Demand_penalty[A1,PowerTrain1]: - demand_satisfied[A1,PowerTrain1]
   + penalty_demand[A1,PowerTrain1] >= 0
 Demand_penalty[A1,Transmission]: - demand_satisfied[A1,Transmission]
   + penalty_demand[A1,Transmission] >= 0
 Demand_penalty[A1,Dashboard]: - demand_satisfied[A1,Dashboard]
   + penalty_demand[A1,Dashboard] >= 0
 Demand_penalty[A1,Vehicle1]: - demand_satisfied[A1,Vehicle1]
   + penalty_demand[A1,Vehicle1] >= 0
 Demand_penalty[S2,PowerTrain2]: - demand_satisfied[S2,PowerTrain2]
   + penalty_demand[S2,PowerTrain2] >= 0
 Demand_penalty[S3,Dashboard]: - demand_satisfied[S3,Dashboard]
   + penalty_demand[S3,Dashboard] >= 0
 Demand_penalty[D2,Vehicle1]: - demand_satisfied[D2,Vehicle1]
   + penalty_demand[D2,Vehicle1] >= 0
 Demand_penalty[D2,Vehicle2]: - demand_satisfied[D2,Vehicle2]
   + penalty_demand[D2,Vehicle2] >= 0
 Demand_penalty[S5,Transmission]: - demand_satisfied[S5,Transmission]
   + penalty_demand[S5,Transmission] >= 0
 Demand_penalty[A2,PowerTrain2]: - demand_satisfied[A2,PowerTrain2]
   + penalty_demand[A2,PowerTrain2] >= 0
 Demand_penalty[A2,Transmission]: - demand_satisfied[A2,Transmission]
   + penalty_demand[A2,Transmission] >= 0
 Demand_penalty[A2,Dashboard]: - demand_satisfied[A2,Dashboard]
   + penalty_demand[A2,Dashboard] >= 0
 Demand_penalty[A2,Vehicle2]: - demand_satisfied[A2,Vehicle2]
   + penalty_demand[A2,Vehicle2] >= 0
 Demand_penalty[S7,Transmission]: - demand_satisfied[S7,Transmission]
   + penalty_demand[S7,Transmission] >= 0
 Demand_penalty[D1,Vehicle1]: - demand_satisfied[D1,Vehicle1]
   + penalty_demand[D1,Vehicle1] >= 0
 Demand_penalty[D1,Vehicle2]: - demand_satisfied[D1,Vehicle2]
   + penalty_demand[D1,Vehicle2] >= 0
 Demand_penalty[C2,Vehicle2]: - demand_satisfied[C2,Vehicle2]
   + penalty_demand[C2,Vehicle2] >= 4500
 Inventory_penalty[S4,Dashboard]: inventory[S4,Dashboard]
   + penalty_inv[S4,Dashboard] >= 0
 Inventory_penalty[S6,Transmission]: inventory[S6,Transmission]
   + penalty_inv[S6,Transmission] >= 0
 Inventory_penalty[C1,Vehicle1]: inventory[C1,Vehicle1]
   + penalty_inv[C1,Vehicle1] >= 0
 Inventory_penalty[S1,PowerTrain1]: inventory[S1,PowerTrain1]
   + penalty_inv[S1,PowerTrain1] >= 0
 Inventory_penalty[A3,PowerTrain2]: inventory[A3,PowerTrain2]
   + penalty_inv[A3,PowerTrain2] >= 0
 Inventory_penalty[A3,Transmission]: inventory[A3,Transmission]
   + penalty_inv[A3,Transmission] >= 0
 Inventory_penalty[A3,Dashboard]: inventory[A3,Dashboard]
   + penalty_inv[A3,Dashboard] >= 0
 Inventory_penalty[A3,Vehicle2]: inventory[A3,Vehicle2]
   + penalty_inv[A3,Vehicle2] >= 0
 Inventory_penalty[A1,PowerTrain1]: inventory[A1,PowerTrain1]
   + penalty_inv[A1,PowerTrain1] >= 0
 Inventory_penalty[A1,Transmission]: inventory[A1,Transmission]
   + penalty_inv[A1,Transmission] >= 0
 Inventory_penalty[A1,Dashboard]: inventory[A1,Dashboard]
   + penalty_inv[A1,Dashboard] >= 0
 Inventory_penalty[A1,Vehicle1]: inventory[A1,Vehicle1]
   + penalty_inv[A1,Vehicle1] >= 0
 Inventory_penalty[S2,PowerTrain2]: inventory[S2,PowerTrain2]
   + penalty_inv[S2,PowerTrain2] >= 0
 Inventory_penalty[S3,Dashboard]: inventory[S3,Dashboard]
   + penalty_inv[S3,Dashboard] >= 0
 Inventory_penalty[D2,Vehicle1]: inventory[D2,Vehicle1]
   + penalty_inv[D2,Vehicle1] >= 0
 Inventory_penalty[D2,Vehicle2]: inventory[D2,Vehicle2]
   + penalty_inv[D2,Vehicle2] >= 0
 Inventory_penalty[S5,Transmission]: inventory[S5,Transmission]
   + penalty_inv[S5,Transmission] >= 0
 Inventory_penalty[A2,PowerTrain2]: inventory[A2,PowerTrain2]
   + penalty_inv[A2,PowerTrain2] >= 0
 Inventory_penalty[A2,Transmission]: inventory[A2,Transmission]
   + penalty_inv[A2,Transmission] >= 0
 Inventory_penalty[A2,Dashboard]: inventory[A2,Dashboard]
   + penalty_inv[A2,Dashboard] >= 0
 Inventory_penalty[A2,Vehicle2]: inventory[A2,Vehicle2]
   + penalty_inv[A2,Vehicle2] >= 0
 Inventory_penalty[S7,Transmission]: inventory[S7,Transmission]
   + penalty_inv[S7,Transmission] >= 0
 Inventory_penalty[D1,Vehicle1]: inventory[D1,Vehicle1]
   + penalty_inv[D1,Vehicle1] >= 0
 Inventory_penalty[D1,Vehicle2]: inventory[D1,Vehicle2]
   + penalty_inv[D1,Vehicle2] >= 0
 Inventory_penalty[C2,Vehicle2]: inventory[C2,Vehicle2]
   + penalty_inv[C2,Vehicle2] >= 0
Bounds
 demand_satisfied[S4,Dashboard] free
 demand_satisfied[S6,Transmission] free
 demand_satisfied[C1,Vehicle1] free
 demand_satisfied[S1,PowerTrain1] free
 demand_satisfied[A3,PowerTrain2] free
 demand_satisfied[A3,Transmission] free
 demand_satisfied[A3,Dashboard] free
 demand_satisfied[A3,Vehicle2] free
 demand_satisfied[A1,PowerTrain1] free
 demand_satisfied[A1,Transmission] free
 demand_satisfied[A1,Dashboard] free
 demand_satisfied[A1,Vehicle1] free
 demand_satisfied[S2,PowerTrain2] free
 demand_satisfied[S3,Dashboard] free
 demand_satisfied[D2,Vehicle1] free
 demand_satisfied[D2,Vehicle2] free
 demand_satisfied[S5,Transmission] free
 demand_satisfied[A2,PowerTrain2] free
 demand_satisfied[A2,Transmission] free
 demand_satisfied[A2,Dashboard] free
 demand_satisfied[A2,Vehicle2] free
 demand_satisfied[S7,Transmission] free
 demand_satisfied[D1,Vehicle1] free
 demand_satisfied[D1,Vehicle2] free
 demand_satisfied[C2,Vehicle2] free
Binaries
 link_product_usage[S6,A3,Transmission]
 link_product_usage[S5,A2,Transmission]
 link_product_usage[S7,A3,Transmission]
 link_product_usage[S6,A1,Transmission]
 link_product_usage[S7,A1,Transmission]
 link_product_usage[S6,A2,Transmission]
 link_product_usage[S5,A3,Transmission]
 link_product_usage[S7,A2,Transmission]
 link_product_usage[S5,A1,Transmission] link_product_usage[S3,A3,Dashboard]
 link_product_usage[S4,A1,Dashboard] link_product_usage[S3,A1,Dashboard]
 link_product_usage[S4,A2,Dashboard] link_product_usage[S3,A2,Dashboard]
 link_product_usage[S4,A3,Dashboard] link_product_usage[S2,A2,PowerTrain2]
 link_product_usage[S2,A3,PowerTrain2]
 link_product_usage[S2,A1,PowerTrain2]
 link_product_usage[S1,A3,PowerTrain1]
 link_product_usage[S1,A1,PowerTrain1]
 link_product_usage[S1,A2,PowerTrain1] link_product_usage[A1,D1,Vehicle1]
 link_product_usage[A1,D2,Vehicle1] link_product_usage[A3,D2,Vehicle2]
 link_product_usage[A2,D1,Vehicle2] link_product_usage[A2,D2,Vehicle2]
 link_product_usage[A3,D1,Vehicle2] link_product_usage[D1,C2,Vehicle1]
 link_product_usage[D2,C1,Vehicle1] link_product_usage[D1,C1,Vehicle1]
 link_product_usage[D2,C2,Vehicle1] link_product_usage[D1,C2,Vehicle2]
 link_product_usage[D2,C1,Vehicle2] link_product_usage[D1,C1,Vehicle2]
 link_product_usage[D2,C2,Vehicle2] prodLine_usage[S4] prodLine_usage[S6]
 prodLine_usage[C1] prodLine_usage[S1] prodLine_usage[A3]
 prodLine_usage[A1] prodLine_usage[S2] prodLine_usage[S3]
 prodLine_usage[D2] prodLine_usage[S5] prodLine_usage[A2]
 prodLine_usage[S7] prodLine_usage[D1] prodLine_usage[C2]
 duedate_exceeded[S6,A3,Transmission] duedate_exceeded[S5,A2,Transmission]
 duedate_exceeded[S7,A3,Transmission] duedate_exceeded[S6,A1,Transmission]
 duedate_exceeded[S7,A1,Transmission] duedate_exceeded[S6,A2,Transmission]
 duedate_exceeded[S5,A3,Transmission] duedate_exceeded[S7,A2,Transmission]
 duedate_exceeded[S5,A1,Transmission] duedate_exceeded[S3,A3,Dashboard]
 duedate_exceeded[S4,A1,Dashboard] duedate_exceeded[S3,A1,Dashboard]
 duedate_exceeded[S4,A2,Dashboard] duedate_exceeded[S3,A2,Dashboard]
 duedate_exceeded[S4,A3,Dashboard] duedate_exceeded[S2,A2,PowerTrain2]
 duedate_exceeded[S2,A3,PowerTrain2] duedate_exceeded[S2,A1,PowerTrain2]
 duedate_exceeded[S1,A3,PowerTrain1] duedate_exceeded[S1,A1,PowerTrain1]
 duedate_exceeded[S1,A2,PowerTrain1] duedate_exceeded[A1,D1,Vehicle1]
 duedate_exceeded[A1,D2,Vehicle1] duedate_exceeded[A3,D2,Vehicle2]
 duedate_exceeded[A2,D1,Vehicle2] duedate_exceeded[A2,D2,Vehicle2]
 duedate_exceeded[A3,D1,Vehicle2] duedate_exceeded[D1,C2,Vehicle1]
 duedate_exceeded[D2,C1,Vehicle1] duedate_exceeded[D1,C1,Vehicle1]
 duedate_exceeded[D2,C2,Vehicle1] duedate_exceeded[D1,C2,Vehicle2]
 duedate_exceeded[D2,C1,Vehicle2] duedate_exceeded[D1,C1,Vehicle2]
 duedate_exceeded[D2,C2,Vehicle2]
End
