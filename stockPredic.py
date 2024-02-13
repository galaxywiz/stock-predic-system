# 아래 예제 실습
#https://data-science-hi.tistory.com/190

# from math import nan
# import pandas as pd
# from sklearn.preprocessing import MinMaxScaler

# import os.path

# import torch
# import torch.nn as nn
# import torch.optim as optim

# import matplotlib.pyplot as plt
# import logger

# device = torch.device('cuda:0')

# class VanillaRNN(nn.Module):
#     def __init__(self, input_size, hidden_size, sequence_length, num_layers):
#         super(VanillaRNN, self).__init__()
#         self.hidden_size = hidden_size
#         self.num_layers = num_layers
#         self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
#         self.fc = nn.Sequential(nn.Linear(hidden_size * sequence_length, 1), nn.Sigmoid())
     
#     def forward(self, x):
#         h0 = torch.zeros(self.num_layers, x.size()[0], self.hidden_size).to(device) # 초기 hidden state 설정하기.
#         out, _ = self.rnn(x, h0) # out: RNN의 마지막 레이어로부터 나온 output feature 를 반환한다. hn: hidden state를 반환한다.
#         out = out.reshape(out.shape[0], -1) # many to many 전략
#         out = self.fc(out)
#         return out

# class StockPredic:
#     def __init__(self, stock_data, stock_price_index, stock_market):
#         self.dtype_ = torch.float
#         print(f'{device} is available')
        
#         self.sequence_length = 5        # 5일 데이터로 6일째를 예측한다

#         # 데이터 셋 관련인데, 어차피 사람이 만든 지표는 모르는거임, 최대한 노이즈 없는 데이터만 넣자
#         self.data_part_orgin_ = ['date','open','high','low','close']
#         self.data_part_x_ = ['open','high','low']
#         self.data_part_y_ = ['close']
#         # 스케일러 분리해야
#         self.data_part_index_ = ['OpenIdx','HighIdx','LowIdx','CloseIdx']

#         # 공용 변수
#         self.model_dir_ = ("./mm_files/%s" % stock_market)
#         self.common_model_file_ = ("%s/stock_predic_model.pt" % (self.model_dir_))
#         self.self_model_file_ = ("%s/stock_predic_model_%s.pt" % (self.model_dir_, stock_data.ticker_))
#         self.study_dir_ = ("./matplot/%s" % stock_market)

#         # 주식 데이터 갖고오기
#         self.stock_data_ = stock_data
#         self.df_ = stock_data.chart_data_[self.data_part_orgin_].copy()

#         # 시장의 인덱스(코스피100, S&P500 같은) 지수 갖고오기
#         self.stock_index_ = stock_price_index
#         self.df_index_ = stock_price_index.chart_data_[self.data_part_orgin_].copy()
#         self.df_index_ = self.df_index_.rename(columns={'open': 'OpenIdx', 'high': 'HighIdx', 'low' : 'LowIdx', 'close' : 'CloseIdx'})
#         self.df_ = pd.merge(self.df_, self.df_index_, how='left', on='date')
        
#         self.data_part_orgin_ = ['open','high','low','close']
#         self.data_part_ = ['OpenIdx','HighIdx','LowIdx','CloseIdx','open','high','low','close']
#         self.data_part_x_ = ['OpenIdx','HighIdx','LowIdx','CloseIdx','open','high','low']

#     def do_study(self, model_name, train_loader, test_loader, input_size, new_model = False):
#         if os.path.isfile(model_name) and new_model == False:
#             self.model_ = torch.load(model_name, map_location=device)
#         else:
#             # RNN 노드 갯수 셋팅
#             num_layers = 4
#             hidden_size = 16
#             self.model_ = VanillaRNN(input_size=input_size,
#                         hidden_size=hidden_size,
#                         sequence_length=self.sequence_length,
#                         num_layers=num_layers).to(device)
       
#         epoch = 200
#         self.__studyModel(model_name, train_loader, epoch)

#         predic, actual = self.predic_price(train_loader, test_loader, self.df_[self.data_part_y_][self.sequence_length:])
#         return predic, actual

#     def predic(self, common_model = False):
#         self.__nomalizing()
#         split = int(self.df_.shape[0] * 0.7)
#         train_loader, test_loader, input_size = self.__prepareTrainData(split)
#         if common_model:
#             predic, actual = self.do_study(self.common_model_file_, train_loader, test_loader, input_size)
#         else:
#             predic, actual = self.do_study(self.self_model_file_, train_loader, test_loader, input_size, new_model=True)

#         arrow = '대기'
#         if actual < predic:
#             arrow = '매수'
#         elif actual > predic:
#             arrow = '매도'
#         logger.info("[%s]의 오늘 :%2.2f. 내일 예측값 : %2.2f => [%s] 추천" % (self.stock_data_.name_, actual, predic, arrow))
#         return predic
        
#     def __nomalizing(self):
#         self.scaler_close_price = MinMaxScaler()
#         self.scaler_close_price.fit_transform(self.df_[self.data_part_y_])

#         self.scaler_ = MinMaxScaler()
#         self.df_[self.data_part_orgin_] = self.scaler_.fit_transform(self.df_[self.data_part_orgin_])
#         self.scaler_index_ = MinMaxScaler()
#         self.df_[self.data_part_index_] = self.scaler_index_.fit_transform(self.df_[self.data_part_index_])
#         print(self.df_)

#     # float형 tensor로 변형, gpu사용가능하게 .to(device)를 사용.
#     def seq_data(self, x, y):
#         x_seq = []
#         y_seq = []
#         for i in range(len(x) - self.sequence_length):
#             x_seq.append(x[i : i + self.sequence_length])
#             y_seq.append(y[i + self.sequence_length])

#         return torch.FloatTensor(x_seq).to(device), torch.FloatTensor(y_seq).to(device).view([-1, 1]) 

#     def __prepareTrainData(self, split):
#         # 훈련 데이터 준비
#         X = self.df_[self.data_part_x_].values
#         y = self.df_[self.data_part_y_].values

#         # 훈련 데이터, 테스트 데이터 셋팅
#         x_seq, y_seq = self.seq_data(X, y)
#         mod = split % self.sequence_length
#         split -= mod

#         x_train_seq = x_seq[:split]
#         y_train_seq = y_seq[:split]
#         x_test_seq = x_seq[split:]
#         y_test_seq = y_seq[split:]
#         print(x_train_seq.size(), y_train_seq.size())
#         print(x_test_seq.size(), y_test_seq.size())

#         # 배치를 해준다, 시계열이므로 셔플을 하면 안된다
#         train = torch.utils.data.TensorDataset(x_train_seq, y_train_seq)
#         test = torch.utils.data.TensorDataset(x_test_seq, y_test_seq)

#         batch_size = 20
#         train_loader = torch.utils.data.DataLoader(dataset=train, batch_size=batch_size, shuffle=False)
#         test_loader = torch.utils.data.DataLoader(dataset=test, batch_size=batch_size, shuffle=False)
#         return train_loader, test_loader, x_seq.size(2)

#     def __studyModel(self, model_name, train_loader, epoch = 200):
#         #regression 문제이기 때문에 loss function 을 MSE 로 두었다. 학습률은 0.001, 에폭은 200으로 설정하였다.
#         criterion = nn.MSELoss()

#         lr = 1e-3
#         num_epochs = epoch
#         optimizer = optim.Adam(self.model_.parameters(), lr=lr)

#         # 모델 학습
#         loss_graph = [] # 그래프 그릴 목적인 loss.
#         n = len(train_loader)

#         for epoch in range(num_epochs):
#             running_loss = 0.0

#             for data in train_loader:
#                 seq, target = data # 배치 데이터.
#                 out = self.model_(seq)   # 모델에 넣고,
#                 loss = criterion(out, target) # output 가지고 loss 구하고,

#                 optimizer.zero_grad() # 
#                 loss.backward() # loss가 최소가 되게하는 
#                 optimizer.step() # 가중치 업데이트 해주고,
#                 running_loss += loss.item() # 한 배치의 loss 더해주고,

#             loss_graph.append(running_loss / n) # 한 epoch에 모든 배치들에 대한 평균 loss 리스트에 담고,
#             if epoch % 100 == 0:
#                 print('[epoch: %d] loss: %.4f'%(epoch, running_loss/n))
        
#         if not os.path.exists(self.model_dir_):
#             os.makedirs(self.model_dir_)
#         torch.save(self.model_, model_name)
        
#         plt.figure(figsize=(20,10))
#         plt.plot(loss_graph)
#         if not os.path.exists(self.study_dir_):
#             os.makedirs(self.study_dir_)
#         file_name = "%s/study_%s_%s.png" % (self.study_dir_, self.stock_data_.name_, self.stock_data_.ticker_)
#         plt.savefig(file_name)

#     def predic_price(self, train_loader, test_loader, actual):
#         with torch.no_grad():
#             train_pred = []
#             test_pred = []

#             for data in train_loader:
#                 seq, target = data
#                 out = self.model_(seq)
#                 train_pred += out.cpu().numpy().tolist()

#             for data in test_loader:
#                 seq, target = data
#                 out = self.model_(seq)
#                 test_pred += out.cpu().numpy().tolist()
            
#         total = train_pred + test_pred

#         actual_inver = self.scaler_close_price.inverse_transform(actual)
#         predic_inver = self.scaler_close_price.inverse_transform(total)

#         self.__plotting(actual_inver, predic_inver)
#         return predic_inver[-1], actual_inver[-1]

#     def __plotting(self, actual, predic):
#         plt.figure(figsize=(20,10))
#  #       plt.plot(np.ones(100)*len(train_pred), np.linspace(0,1,100), '--', linewidth=0.6)
#         plt.plot(actual, color='red', linestyle='dashed')
#         plt.plot(predic, 'b', linewidth=0.6)

#         plt.legend(['actual', 'prediction'])
#         file_name = "%s/predic_%s_%s.png" % (self.study_dir_, self.stock_data_.name_, self.stock_data_.ticker_)
#         plt.savefig(file_name)
#         print("%s file save" % file_name)