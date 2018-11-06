class TweetsController < ApplicationController

  # GET: /tweets
  get "/tweets" do
    erb :"/tweets/index.html"
  end

  # GET: /tweets/new
  get "/tweets/new" do
    erb :"/tweets/new.html"
  end

  # POST: /tweets
  post "/tweets" do
    redirect "/tweets"
  end

  # GET: /tweets/5
  get "/tweets/:id" do
    erb :"/tweets/show.html"
  end

  # GET: /tweets/5/edit
  get "/tweets/:id/edit" do
    erb :"/tweets/edit.html"
  end

  # PATCH: /tweets/5
  patch "/tweets/:id" do
    redirect "/tweets/:id"
  end

  # DELETE: /tweets/5/delete
  delete "/tweets/:id/delete" do
    redirect "/tweets"
  end
end
