class DashboardsController < ApplicationController
  # GET: /dashboards
  get "/dashboards" do
    @title = "Gráficos"
    # @data = []
    #
    # (1..31).to_a.each do |day|
    #   (0..23).to_a.each do |hour|
    #     infos = InfosInHour.where(time: Time.new(2016, 1, day, hour, 0, 0))
    #
    #     hour_hash = {}
    #     hour_hash["hour"] = "#{day}(#{hour}h)"
    #     hour_hash["all_tweets"] = infos.pluck(:all_tweets).sum
    #     hour_hash["related_tweets"] = infos.pluck(:related_tweets).sum
    #     hour_hash["gauge_measures"] = infos.pluck(:gauge_measures).sum
    #
    #     @data << hour_hash
    #   end
    # end
    #
    # @data = @data.to_json

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

    # individual tweets count, related tweets count and rainfall measure in hour
    @individual_infos_in_hour = InfosInHour.where(gauge_id: @active_gauge.id)
    @individual_infos_in_hour = @individual_infos_in_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    @individual_infos_in_hour = @individual_infos_in_hour.to_json
    # individual tweets count, related tweets count and rainfall measure in half hour
    @individual_infos_in_half_hour = InfosInHalfHour.where(gauge_id: @active_gauge.id)
    @individual_infos_in_half_hour = @individual_infos_in_half_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    @individual_infos_in_half_hour = @individual_infos_in_half_hour.to_json

    erb :"/dashboards/charts.html"
  end

  post "/dashboards" do
    @gauges = Gauge.all.order(:name)
    @active_gauge = (params[:active_gauge] != nil && params[:active_gauge].to_i > 0 && params[:active_gauge].to_i < 82) ? Gauge.find(params[:active_gauge]) : @gauges.find(28)

    # individual tweets count, related tweets count and rainfall measure in hour
    @individual_infos_in_hour = InfosInHour.where(gauge_id: @active_gauge.id)
    @individual_infos_in_hour = @individual_infos_in_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    # @individual_infos_in_hour = @individual_infos_in_hour.to_json
    # individual tweets count, related tweets count and rainfall measure in half hour
    @individual_infos_in_half_hour = InfosInHalfHour.where(gauge_id: @active_gauge.id)
    @individual_infos_in_half_hour = @individual_infos_in_half_hour.map {|i| {time: "#{i.time.day} (#{i.time.hour}h#{i.time.min})", all_tweets: i.all_tweets, related_tweets: i.related_tweets, gauge_measures: i.gauge_measures}}
    # @individual_infos_in_half_hour = @individual_infos_in_half_hour.to_json

    [@individual_infos_in_hour, @individual_infos_in_half_hour].to_json
  end
end
