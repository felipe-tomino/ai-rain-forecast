class DashboardsController < ApplicationController
  # GET: /dashboards
  get "/dashboards" do
    erb :"/dashboards/charts.html"
  end
end
