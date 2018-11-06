class GaugesMeasuresController < ApplicationController

  # GET: /gauges_measures
  get "/gauges_measures" do
    erb :"/gauges_measures/index.html"
  end

  # GET: /gauges_measures/new
  get "/gauges_measures/new" do
    erb :"/gauges_measures/new.html"
  end

  # POST: /gauges_measures
  post "/gauges_measures" do
    redirect "/gauges_measures"
  end

  # GET: /gauges_measures/5
  get "/gauges_measures/:id" do
    erb :"/gauges_measures/show.html"
  end

  # GET: /gauges_measures/5/edit
  get "/gauges_measures/:id/edit" do
    erb :"/gauges_measures/edit.html"
  end

  # PATCH: /gauges_measures/5
  patch "/gauges_measures/:id" do
    redirect "/gauges_measures/:id"
  end

  # DELETE: /gauges_measures/5/delete
  delete "/gauges_measures/:id/delete" do
    redirect "/gauges_measures"
  end
end
