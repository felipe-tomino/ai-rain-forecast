class DashboardsController < ApplicationController
  # GET: /dashboards
  get "/dashboards" do
    @data = []

    (1..31).to_a.each do |day|
      (0..23).to_a.each do |hour|
        infos = InfosInHour.where(hour: Time.new(2016, 1, day, hour, 0, 0))

        hour_hash = {}
        hour_hash["hour"] = "#{day}(#{hour}h)"
        hour_hash["all_tweets"] = infos.pluck(:all_tweets).sum
        hour_hash["related_tweets"] = infos.pluck(:related_tweets).sum
        hour_hash["gauge_measures"] = infos.pluck(:gauge_measures).sum

        @data << hour_hash
      end
    end

    @data = @data.to_json

    erb :"/dashboards/charts.html"
  end
end
