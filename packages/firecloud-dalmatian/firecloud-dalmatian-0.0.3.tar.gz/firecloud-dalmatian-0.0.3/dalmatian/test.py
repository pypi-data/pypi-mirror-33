import pandas as pd
import imp
import dalmatian

# imp.reload(dalmatian.core); imp.reload(dalmatian.wmanager); imp.reload(dalmatian);

test_wm = dalmatian.WorkspaceManager('broad-firecloud-gtex/dalmatian_test_0218')
test_wm.create_workspace()

upload_df = pd.DataFrame(np.array([
    ['participant1', 'participant1', 'participant2', 'participant2'],
    ['all_samples', 'all_samples', 'all_samples', 'all_samples'],
    ['a','b','c','d'],
    ['aa','bb','cc','dd']
]).T, index=['sample1', 'sample2', 'sample3', 'sample4'], columns=['participant_id', 'sample_set_id', 'attr1', 'attr2'])
upload_df.index.name = 'sample_id'

test_wm.upload_samples(upload_df)

test_wm.update_sample_attributes({'Tumor':'tumor_sample', 'Normal':'normal_sample'}, 'sample1')
test_wm.delete_entity_attributes('sample', test_wm.get_samples()['Normal'])
test_wm.delete_entity_attributes('sample', test_wm.get_samples()[['Normal', 'Tumor']])
test_wm.delete_entity_attributes('sample', ['Tumor', 'Normal'], entity_id='sample1')

test_wm.update_sample_attributes(pd.Series(data=['Normal', 'Tumor', 'Normal', 'Tumor'], index=['sample1', 'sample2', 'sample3', 'sample4'], name='sample_type'))
test_wm.make_pairs()

test_wm.update_participant_samples_and_pairs()
test_wm.get_participants()
test_wm.get_pairs()

test_wm.delete_sample_set('all_samples')
test_wm.delete_participant('participant1')
test_wm.delete_participant('participant1', delete_dependencies=True)
test_wm.delete_entity_attributes('sample', test_wm.get_samples()['attr2'])
test_wm.update_sample_set('all_samples', test_wm.get_samples().index)


