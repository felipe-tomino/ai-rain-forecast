class DashboardsController < ApplicationController
  # GET: /dashboards
  get "/dashboards" do
    # @data = []
    #
    # (1..31).to_a.each do |day|
    #   (0..23).to_a.each do |hour|
    #     hour_tweets = Tweet.where('posted_at > ?', Time.new(2016, 1, day, hour, 0, 0)).
    #                         where('posted_at <= ?', Time.new(2016, 1, day, (hour+1), 0, 0))
    #     hour_gauges_measures = GaugesMeasure.where('measured_at > ?', Time.new(2016, 1, day, hour, 0, 0)).
    #                                           where('measured_at <= ?', Time.new(2016, 1, day, (hour+1), 0, 0))
    #
    #     hour_hash = {}
    #     hour_hash["hour"] = "#{day}(#{hour}h)"
    #     hour_hash["all_tweets"] = hour_tweets.count
    #     hour_hash["related_tweets"] = hour_tweets.where(rain_related: true).count
    #     hour_hash["gauge_measures"] = hour_gauges_measures.pluck(:measure).sum
    #
    #     @data << hour_hash
    #   end
    # end
    #
    # @data = @data.to_json

    erb :"/dashboards/charts.html"
  end
end
