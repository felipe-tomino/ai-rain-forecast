class GaugesController < ApplicationController
  # GET: /gauges/map
  get "/gauges/map" do
    erb :"/gauges/map.html", {layout: false}
  end

  # GET: /gauges
  get "/gauges" do
    erb :"/gauges/index.html"
  end

  # GET: /gauges/new
  get "/gauges/new" do
    erb :"/gauges/new.html"
  end

  # POST: /gauges
  post "/gauges" do
    redirect "/gauges"
  end

  # GET: /gauges/5
  get "/gauges/:id" do
    erb :"/gauges/show.html"
  end

  # GET: /gauges/5/edit
  get "/gauges/:id/edit" do
    erb :"/gauges/edit.html"
  end

  # PATCH: /gauges/5
  patch "/gauges/:id" do
    redirect "/gauges/:id"
  end

  # DELETE: /gauges/5/delete
  delete "/gauges/:id/delete" do
    redirect "/gauges"
  end
end
