class DashboardsController < ApplicationController
  require 'csv'

  # individual tweets count, related tweets count and rainfall measure in hour
  def get_individual_infos_in_hour(gauge)
    individual_infos_in_hour = InfosInHour.where(gauge_id: gauge.id)
    individual_infos_in_hour = individual_infos_in_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    individual_infos_in_hour
  end
  # individual tweets count, related tweets count and rainfall measure in half hour
  def get_individual_infos_in_half_hour(gauge)
    individual_infos_in_half_hour = InfosInHalfHour.where(gauge_id: gauge.id)
    individual_infos_in_half_hour = individual_infos_in_half_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    individual_infos_in_half_hour
  end

  # GET: /charts
  get "/charts" do
    @page = "charts"
    @title = "Gráficos"

    @gauges = Gauge.all.order(:name)
    @active_gauge = (params[:active_gauge] != nil && params[:active_gauge].to_i > 0 && params[:active_gauge].to_i < 82) ? Gauge.find(params[:active_gauge]) : @gauges.find(28)

    # global tweets count, related tweets count and rainfall measure in hour
    @global_infos_in_hour = GlobalInfosInHour.all
    @global_infos_in_hour = @global_infos_in_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    @global_infos_in_hour = @global_infos_in_hour.to_json
    # global tweets count, related tweets count and rainfall measure in half hour
    @global_infos_in_half_hour = GlobalInfosInHalfHour.all
    @global_infos_in_half_hour = @global_infos_in_half_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    @global_infos_in_half_hour = @global_infos_in_half_hour.to_json

    @individual_infos_in_hour = get_individual_infos_in_hour(@active_gauge).to_json
    @individual_infos_in_half_hour = get_individual_infos_in_half_hour(@active_gauge).to_json

    erb :"/dashboards/charts.html"
  end

  get "/map" do
    @page = "map"
    @title = "Mapa de sensores"
    @gauges = Gauge.all.order(:name)

    @gauges_infos = InfosInHalfHour.all.group(:gauge_id).order(:gauge_id).pluck("gauge_id, sum(all_tweets), sum(related_tweets), sum(gauge_measures)")

    erb :"/dashboards/map.html"
  end

  get "/datasets" do
    @page = "datasets"
    @title = "Datasets de Treino e Teste"

    clf = params['clf']
    attribs = params['attr']
    gauge = params['gauge']
    split = params['split']

    @train_dataset = CSV.read("./python/SVR_cv_notn/ymdhmtrrpr/gauge1_split1_train.csv", { col_sep: ";" })
    @test_dataset = CSV.read("./python/SVR_cv_notn/ymdhmtrrpr/gauge1_split1_test.csv", { col_sep: ";" })

    erb :"/dashboards/datasets.html"
  end

  post "/datasets" do
    clf = params['clf']
    attribs = params['attr']
    gauge = params['gauge']
    split = params['split']

    train_dataset = CSV.read("./python/#{clf}/#{attribs}/gauge#{gauge}_split#{split}_train.csv", { col_sep: ";" })
    test_dataset = CSV.read("./python/#{clf}/#{attribs}/gauge#{gauge}_split#{split}_test.csv", { col_sep: ";" })

    [train_dataset, test_dataset].to_json
  end

  get "/classification-results" do
    @page = "classification-results"
    @title = "Resultados das Classificações"

    @gauges = Gauge.all.order(:id).pluck(:id, :name, :cod).map{ |gauge| "#{gauge[1]} (#{gauge[2]})"}

    @svr_notn_ymdhmtrrpr_results = CSV.read("./python/SVR_cv_notn/ymdhmtrrpr/svr_scores.csv", { col_sep: ";" })
    @svr_notn_hmtrrpr_results = CSV.read("./python/SVR_cv_notn/hmtrrpr/svr_scores.csv", { col_sep: ";" })
    @svr_notn_trrpr_results = CSV.read("./python/SVR_cv_notn/trrpr/svr_scores.csv", { col_sep: ";" })
    @svr_notn_ymdhmtrr_results = CSV.read("./python/SVR_cv_notn/ymdhmtrr/svr_scores.csv", { col_sep: ";" })
    @svr_notn_hmtrr_results = CSV.read("./python/SVR_cv_notn/hmtrr/svr_scores.csv", { col_sep: ";" })
    @svr_notn_trr_results = CSV.read("./python/SVR_cv_notn/trr/svr_scores.csv", { col_sep: ";" })

    @svr_ymdhmtrrpr_results = CSV.read("./python/SVR_cv/ymdhmtrrpr/svr_scores.csv", { col_sep: ";" })
    @svr_hmtrrpr_results = CSV.read("./python/SVR_cv/hmtrrpr/svr_scores.csv", { col_sep: ";" })
    @svr_trrpr_results = CSV.read("./python/SVR_cv/trrpr/svr_scores.csv", { col_sep: ";" })
    @svr_ymdhmtrr_results = CSV.read("./python/SVR_cv/ymdhmtrr/svr_scores.csv", { col_sep: ";" })
    @svr_hmtrr_results = CSV.read("./python/SVR_cv/hmtrr/svr_scores.csv", { col_sep: ";" })
    @svr_trr_results = CSV.read("./python/SVR_cv/trr/svr_scores.csv", { col_sep: ";" })

    @svc_ymdhmtrrpr_results = CSV.read("./python/SVC_cv/ymdhmtrrpr/svc_scores.csv", { col_sep: ";" })
    @svc_hmtrrpr_results = CSV.read("./python/SVC_cv/hmtrrpr/svc_scores.csv", { col_sep: ";" })
    @svc_trrpr_results = CSV.read("./python/SVC_cv/trrpr/svc_scores.csv", { col_sep: ";" })
    @svc_ymdhmtrr_results = CSV.read("./python/SVC_cv/ymdhmtrr/svc_scores.csv", { col_sep: ";" })
    @svc_hmtrr_results = CSV.read("./python/SVC_cv/hmtrr/svc_scores.csv", { col_sep: ";" })
    @svc_trr_results = CSV.read("./python/SVC_cv/trr/svc_scores.csv", { col_sep: ";" })

    @svr_notn_ymdhmtrrpr_results = @svr_notn_ymdhmtrrpr_results[1..@svr_notn_ymdhmtrrpr_results.length]
    @svr_notn_hmtrrpr_results = @svr_notn_hmtrrpr_results[1..@svr_notn_hmtrrpr_results.length]
    @svr_notn_trrpr_results = @svr_notn_trrpr_results[1..@svr_notn_trrpr_results.length]
    @svr_notn_ymdhmtrr_results = @svr_notn_ymdhmtrr_results[1..@svr_notn_ymdhmtrr_results.length]
    @svr_notn_hmtrr_results = @svr_notn_hmtrr_results[1..@svr_notn_hmtrr_results.length]
    @svr_notn_trr_results = @svr_notn_trr_results[1..@svr_notn_trr_results.length]
    @svr_ymdhmtrrpr_results = @svr_ymdhmtrrpr_results[1..@svr_ymdhmtrrpr_results.length]
    @svr_hmtrrpr_results = @svr_hmtrrpr_results[1..@svr_hmtrrpr_results.length]
    @svr_trrpr_results = @svr_trrpr_results[1..@svr_trrpr_results.length]
    @svr_ymdhmtrr_results = @svr_ymdhmtrr_results[1..@svr_ymdhmtrr_results.length]
    @svr_hmtrr_results = @svr_hmtrr_results[1..@svr_hmtrr_results.length]
    @svr_trr_results = @svr_trr_results[1..@svr_trr_results.length]
    @svc_ymdhmtrrpr_results = @svc_ymdhmtrrpr_results[1..@svc_ymdhmtrrpr_results.length]
    @svc_hmtrrpr_results = @svc_hmtrrpr_results[1..@svc_hmtrrpr_results.length]
    @svc_trrpr_results = @svc_trrpr_results[1..@svc_trrpr_results.length]
    @svc_ymdhmtrr_results = @svc_ymdhmtrr_results[1..@svc_ymdhmtrr_results.length]
    @svc_hmtrr_results = @svc_hmtrr_results[1..@svc_hmtrr_results.length]
    @svc_trr_results = @svc_trr_results[1..@svc_trr_results.length]

    erb :"/dashboards/classification_results.html"
  end

  post "/individual_chart" do
    gauges = Gauge.all.order(:name)
    active_gauge = (params[:active_gauge] != nil && params[:active_gauge].to_i > 0 && params[:active_gauge].to_i < 82) ? Gauge.find(params[:active_gauge]) : @gauges.find(28)

    individual_infos_in_hour = get_individual_infos_in_hour(active_gauge)
    individual_infos_in_half_hour = get_individual_infos_in_half_hour(active_gauge)

    [individual_infos_in_hour, individual_infos_in_half_hour].to_json
  end

  post "/map_individual_info" do
    gauges = Gauge.all.order(:name)
    active_gauge = (params[:active_gauge] != nil && params[:active_gauge].to_i > 0 && params[:active_gauge].to_i < 82) ? Gauge.find(params[:active_gauge]) : @gauges.find(28)

    individual_infos_in_half_hour = get_individual_infos_in_half_hour(active_gauge)

    tweets_count = individual_infos_in_half_hour.map{ |n| n[:all_tweets]}.sum
    related_tweets_count = individual_infos_in_half_hour.map{ |n| n[:related_tweets]}.sum
    precision = related_tweets_count.to_f / InfosInHalfHour.all.pluck(:all_tweets).sum.to_f
    recall = related_tweets_count.to_f / InfosInHalfHour.all.pluck(:related_tweets).sum.to_f
    total_rainfall = individual_infos_in_half_hour.map{ |n| n[:gauge_measures]}.sum

    { gauge_name: active_gauge.name,
      gauge_cod: active_gauge.cod,
      dataProvider: individual_infos_in_half_hour,
      tweets_count: tweets_count,
      related_tweets_count: related_tweets_count,
      precision: precision,
      recall: recall,
      total_rainfall: total_rainfall
    }.to_json
  end
end
