class DashboardsController < ApplicationController
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
    @gauges = Gauge.all.order(:name)

    erb :"/dashboards/map.html"
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
